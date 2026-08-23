/**
 * ndvi_export_grid.js
 *
 * Task 3 + 4 data collection. Two exports:
 *
 *   field_ndvi.csv       field_id,date,ndvi        (Nov-Apr, the FEATURES)
 *   field_offseason.csv  field_id,offseason_ndvi   (May-Jun, the LABELS)
 *
 * ---------------------------------------------------------------------------
 * WHY TWO WINDOWS
 * ---------------------------------------------------------------------------
 * The classifier only ever sees Nov-Apr. May-June is data it has never touched,
 * which makes it valid as ground truth rather than circular.
 *
 * In May-June the rabi crop has been harvested and kharif has not established.
 * An annual field (wheat, mustard, gram) is bare soil, NDVI ~0.15-0.25.
 * Sugarcane is a 12-18 month crop and is still standing, NDVI ~0.5-0.75.
 *
 * So off-season NDVI gives an INDEPENDENT perennial-vs-annual label. That is a
 * real labelled set, obtained from data rather than from guessing at a basemap.
 *
 * It does NOT separate wheat from mustard from gram. Nothing available in a
 * hackathon does. Those stay baseline-only and you say so out loud.
 * ---------------------------------------------------------------------------
 */

// ===========================================================================
// 1. SAMPLE GRID
// ===========================================================================
// 80 small boxes spread across the study area. Some will land on villages,
// roads and canals - that is fine and realistic. The pipeline drops fields
// with too few observations, and non-cropland is a legitimate negative class.

var BOX = 0.0012;          // ~130m, about one parcel. Do not enlarge.

var lons = ee.List.sequence(77.66, 77.84, 0.02);
var lats = ee.List.sequence(29.36, 29.47, 0.015);

var raw = ee.FeatureCollection(lons.map(function (x) {
  return lats.map(function (y) {
    x = ee.Number(x);
    y = ee.Number(y);
    return ee.Feature(ee.Geometry.Rectangle([
      x, y, x.add(BOX), y.add(BOX)
    ]));
  });
}).flatten());

var rawList = raw.toList(raw.size());
var FIELDS = ee.FeatureCollection(
  ee.List.sequence(0, raw.size().subtract(1)).map(function (i) {
    i = ee.Number(i);
    return ee.Feature(rawList.get(i))
      .set('field_id', ee.String('F').cat(i.format('%03d')));
  })
);

print('Sample fields:', FIELDS.size());


// ===========================================================================
// 2. SHARED CLOUD MASK
// ===========================================================================

function maskS2(img) {
  var scl = img.select('SCL');
  var good = scl.eq(4).or(scl.eq(5)).or(scl.eq(6)).or(scl.eq(7));
  return img.updateMask(good);
}

function ndviCollection(start, end) {
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate(start, end)
    .filterBounds(FIELDS)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
    .map(maskS2)
    .map(function (img) {
      var ndvi = img.normalizedDifference(['B8', 'B4']).rename('ndvi');
      return ee.Image(ndvi.copyProperties(img, ['system:time_start']));
    });
}


// ===========================================================================
// 3. EXPORT A: IN-SEASON TIME SERIES (the features)
// ===========================================================================
// Nov 1 start, NOT Oct 1. In early October the kharif crop is still standing
// and its tail corrupts the front of every curve.

var inSeason = ndviCollection('2024-11-01', '2025-04-15');
print('In-season scenes:', inSeason.size());

var series = inSeason.map(function (img) {
  var d = ee.Date(img.get('system:time_start')).format('YYYY-MM-dd');
  return img.reduceRegions({
    collection: FIELDS,
    reducer: ee.Reducer.mean(),
    scale: 10
  }).map(function (f) {
    return ee.Feature(null, {
      field_id: f.get('field_id'),
      date: d,
      ndvi: f.get('mean')
    });
  });
}).flatten().filter(ee.Filter.notNull(['ndvi']));

Export.table.toDrive({
  collection: series,
  description: 'field_ndvi',
  fileFormat: 'CSV',
  selectors: ['field_id', 'date', 'ndvi']
});


// ===========================================================================
// 4. EXPORT B: OFF-SEASON MEDIAN (the labels)
// ===========================================================================

var offSeason = ndviCollection('2025-05-10', '2025-06-15').median();

var labels = offSeason.reduceRegions({
  collection: FIELDS,
  reducer: ee.Reducer.mean(),
  scale: 10
}).map(function (f) {
  return ee.Feature(null, {
    field_id: f.get('field_id'),
    offseason_ndvi: f.get('mean')
  });
}).filter(ee.Filter.notNull(['offseason_ndvi']));

Export.table.toDrive({
  collection: labels,
  description: 'field_offseason',
  fileFormat: 'CSV',
  selectors: ['field_id', 'offseason_ndvi']
});


// ===========================================================================
// 5. VISUAL CHECK
// ===========================================================================

Map.centerObject(FIELDS, 12);
Map.addLayer(offSeason, {min: 0, max: 0.9, palette: ['brown', 'yellow', 'green']},
             'off-season NDVI (green = still standing = sugarcane)');
Map.addLayer(FIELDS, {color: 'red'}, 'sample fields');
