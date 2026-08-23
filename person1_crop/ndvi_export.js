/**
 * ndvi_export.js
 *
 * Paste this whole file into https://code.earthengine.google.com and hit Run.
 * It exports exactly the CSV that crop_classify.py expects:
 *
 *     field_id,date,ndvi
 *
 * You do NOT need Person 2 to run this. Get your own data, get unblocked.
 *
 * ---------------------------------------------------------------------------
 * SETUP (once)
 * ---------------------------------------------------------------------------
 * 1. Go to https://code.earthengine.google.com
 * 2. Sign in with a Google account. If it says you need to register, pick
 *    "Unpaid usage / Academic or research" - approval is usually instant.
 * 3. Paste this file in, press Run, then go to the "Tasks" tab on the right
 *    and click RUN on the export task. CSV lands in your Google Drive in a
 *    few minutes.
 * ---------------------------------------------------------------------------
 */

// ===========================================================================
// 1. YOUR FIELDS
// ===========================================================================
// Option A (fastest, use this today): hardcoded test rectangles.
// These are small boxes in the Muzaffarnagar / Meerut belt of western UP,
// which is wheat and sugarcane country. Replace the coordinates with your
// actual pilot area when you know it. Format is [west, south, east, north].

// Boxes are ~0.0012 degrees, roughly 130m, which is about one real parcel.
// Do NOT make these bigger. At 0.006 degrees (600m) you average twenty-odd
// separate fields together and the peak gets smeared flat.
//
// F001 and F004 were relocated after the originals turned out to be
// settlement / permanent fallow (NDVI never rose above 0.38).

var FIELDS = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Rectangle([77.7130, 29.4055, 77.7142, 29.4067]), {field_id: 'F001'}),
  ee.Feature(ee.Geometry.Rectangle([77.7224, 29.4124, 77.7236, 29.4136]), {field_id: 'F002'}),
  ee.Feature(ee.Geometry.Rectangle([77.7424, 29.3974, 77.7436, 29.3986]), {field_id: 'F003'}),
  ee.Feature(ee.Geometry.Rectangle([77.7712, 29.4168, 77.7724, 29.4180]), {field_id: 'F004'}),
  ee.Feature(ee.Geometry.Rectangle([77.7824, 29.3874, 77.7836, 29.3886]), {field_id: 'F005'}),
  ee.Feature(ee.Geometry.Rectangle([77.8024, 29.4324, 77.8036, 29.4336]), {field_id: 'F006'})
]);

// Option B (later): draw your own polygons with the geometry tool in the
// top-left of the map, name the layer "fields", then uncomment:
// var FIELDS = fields.map(function(f, i) { return f.set('field_id', 'F' + i); });

// Option C (real pipeline): upload a shapefile as an EE asset, then:
// var FIELDS = ee.FeatureCollection('projects/YOUR_PROJECT/assets/your_fields');


// ===========================================================================
// 2. SEASON WINDOW
// ===========================================================================
// Rabi: Nov 1 to Apr 15.  Kharif: Jun 1 to Nov 30.
// Must match the --season flag you pass to crop_classify.py.
//
// NOTE ON THE RABI START DATE: do NOT start this on Oct 1. In northern India
// the kharif crop (rice, sugarcane) is still standing in early October, so an
// October start puts the tail of the PREVIOUS crop at the front of every
// curve. The classifier then tries to fit two crops with one profile and
// confidence collapses. Nov 1 is late enough that fields are cleared.
// Tradeoff: mustard is sown mid-October, so you lose its first few weeks. Its
// peak and senescence still land inside the window, which is what matters.

var START = '2024-11-01';
var END   = '2025-04-15';


// ===========================================================================
// 3. CLOUD MASKING
// ===========================================================================
// Sentinel-2 ships a scene classification band (SCL). Keep only the classes
// that are actually ground: vegetation, bare soil, water, unclassified.
// Everything else is cloud, shadow, snow or saturated pixels.

function maskS2(img) {
  var scl = img.select('SCL');
  var good = scl.eq(4)   // vegetation
    .or(scl.eq(5))       // bare soil
    .or(scl.eq(6))       // water
    .or(scl.eq(7));      // unclassified
  return img.updateMask(good);
}


// ===========================================================================
// 4. BUILD THE NDVI COLLECTION
// ===========================================================================

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate(START, END)
  .filterBounds(FIELDS)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
  .map(maskS2)
  .map(function(img) {
    // NDVI = (NIR - Red) / (NIR + Red) = (B8 - B4) / (B8 + B4)
    var ndvi = img.normalizedDifference(['B8', 'B4']).rename('ndvi');
    return ee.Image(ndvi.copyProperties(img, ['system:time_start']));
  });

print('Sentinel-2 scenes found:', s2.size());


// ===========================================================================
// 5. MEAN NDVI PER FIELD PER DATE
// ===========================================================================

var samples = s2.map(function(img) {
  var d = ee.Date(img.get('system:time_start')).format('YYYY-MM-dd');
  return img.reduceRegions({
    collection: FIELDS,
    reducer: ee.Reducer.mean(),
    scale: 10                       // Sentinel-2 native resolution, metres
  }).map(function(f) {
    // Build the feature explicitly rather than using .select(). When a field is
    // fully cloud-masked on a given date, reduceRegions omits the 'mean'
    // property altogether instead of returning null, and .select() then fails
    // with "Selected a different number of properties than names".
    // ee.Feature(null, ...) also drops geometry, which keeps the CSV small.
    return ee.Feature(null, {
      field_id: f.get('field_id'),
      date: d,
      ndvi: f.get('mean')
    });
  });
}).flatten().filter(ee.Filter.notNull(['ndvi']));

print('Sample rows (first 10):', samples.limit(10));


// ===========================================================================
// 6. EXPORT
// ===========================================================================
// After you press Run, go to the Tasks tab on the right and click RUN.

Export.table.toDrive({
  collection: samples,
  description: 'field_ndvi',
  fileFormat: 'CSV',
  selectors: ['field_id', 'date', 'ndvi']   // exact column order, exact names
});


// ===========================================================================
// 7. OPTIONAL: look at the map to sanity check your boxes are on farmland
// ===========================================================================

Map.centerObject(FIELDS, 12);
Map.addLayer(FIELDS, {color: 'red'}, 'fields');
Map.addLayer(
  s2.median().clip(FIELDS.geometry().bounds()),
  {min: 0, max: 0.9, palette: ['brown', 'yellow', 'green']},
  'median NDVI'
);
