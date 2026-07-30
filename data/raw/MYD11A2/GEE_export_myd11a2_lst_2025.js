/**
 * Export MODIS MYD11A2 Land Surface Temperature (LST)
 *
 * Dataset:
 *   MODIS/061/MYD11A2
 *
 * Temporal coverage:
 *   2025-04-01 to 2025-09-01
 *
 * Spatial extent:
 *   Vietnam
 *
 * Output:
 *   MYD11A2_A2025.tif
 *
 * Projection:
 *   World Mollweide (ESRI:54009)
 */
// =============================================
// MODIS MYD11A2 Land Surface Temperature (LST)
// =============================================
var lst = ee.ImageCollection("MODIS/061/MYD11A2")
    .filterDate('2025-04-01', '2025-09-01')
    .select('LST_Day_1km');

// Generate the median LST composite
var lstMedian = lst.median()
    .unmask(-9999)
    .int16();

// =============================================
// Export region (WGS84)
// Covers the entire territory of Vietnam
// =============================================
var region = ee.Geometry.Rectangle([
    101.0,   // Minimum longitude
    7.5,     // Minimum latitude
    110.5,   // Maximum longitude
    24.5     // Maximum latitude
]);

Map.centerObject(region, 6);

Map.addLayer(
    lstMedian,
    {
        min: 13000,
        max: 17000
    },
    'MYD11A2 LST'
);

Map.addLayer(region, {color: 'red'}, 'Export Region');

// =============================================
// Export settings
// =============================================

// Define the World Mollweide projection (equivalent to ESRI:54009)
var mollweideWKT = 'PROJCS["World_Mollweide",' +
  'GEOGCS["GCS_WGS_1984",' +
  'DATUM["D_WGS_1984",' +
  'SPHEROID["WGS_1984",6378137.0,298.257223563]],' +
  'PRIMEM["Greenwich",0.0],' +
  'UNIT["Degree",0.0174532925199433]],' +
  'PROJECTION["Mollweide"],' +
  'PARAMETER["False_Easting",0.0],' +
  'PARAMETER["False_Northing",0.0],' +
  'PARAMETER["Central_Meridian",0.0],' +
  'UNIT["Meter",1.0]]';

Export.image.toDrive({

    image: lstMedian,

    description: 'Export_MYD11A2_2025',

    fileNamePrefix: 'MYD11A2_A2025',

    region: region,

    crs: mollweideWKT,

    scale: 1000,

    maxPixels: 1e13,

    fileFormat: 'GeoTIFF',

    formatOptions: {
        noData: -9999
    }

});
