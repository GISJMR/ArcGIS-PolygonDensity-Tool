# -----------------------------------------------
# Name: Polygon Density Tool
# Purpose: Counts the number of overlapping polygons
# Author: James M Roden (based on the model by Dale Honeycutt at ESRI - "Spaghetti and Meatballs")
# Created: Jan 2018
# ArcGIS Version: 10.3
# Python Version 2.6
# PEP8
# -----------------------------------------------

try:
    import arcpy
    import os
    import sys
    import traceback

    # arcpy environment settings
    arcpy.env.workspace = r'in_memory'
    arcpy.env.scratchWorkspace = r'in_memory'

    # ArcGIS tool parameters
    overlapping_polygons = arcpy.GetParameterAsText(0)
    output_polygons = arcpy.GetParameterAsText(1)

    # Create the 'spaghetti'
    arcpy.CreateFeatureclass_management(r'in_memory', "Empty_Point", "POINT")  # Trick to remove fields
    spaghetti = arcpy.FeatureToPolygon_management(overlapping_polygons, None, label_features="Empty_Point")

    arcpy.AddMessage("Created 'spaghetti' polygons")

    # Create the 'meatballs'
    meatballs = arcpy.FeatureToPoint_management(spaghetti, None, "INSIDE")

    arcpy.AddMessage("Created 'meatball' points")

    # Overlay the meatball centroids with the original overlapping polygons to get a count of how many polygons overlap
    # each meatball point.
    meatballs_count = arcpy.SpatialJoin_analysis(meatballs, overlapping_polygons, None)

    arcpy.AddMessage("Spatial Join Complete")

    # Join the Join_Count (number of overlapping polygons) field to the spaghetti
    arcpy.JoinField_management(spaghetti, "OID", meatballs_count, "OID", ["Join_Count"])

    arcpy.AddMessage("Join Field Complete")

    # Alter Field Name
    arcpy.AlterField_management(spaghetti, "Join_Count", "COVERAGE", "COVERAGE")

    # Remove artifacts (i.e. polygons with a join count of 0)
    spaghetti = arcpy.MakeFeatureLayer_management(spaghetti, None, "COVERAGE > 0")

    # Output polygons
    arcpy.CopyFeatures_management(spaghetti, output_polygons)

except:
    e = sys.exc_info()[1]
    arcpy.AddError(e.args[0])
    tb = sys.exc_info()[2]  # Traceback object
    tbinfo = traceback.format_tb(tb)[0]  # Traceback string
    # Concatenate error information and return to GP window
    pymsg = ('PYTHON ERRORS:\nTraceback info:\n' + tbinfo + '\nError Info: \n'
             + str(sys.exc_info()[1]))
    msgs = 'ArcPy ERRORS:\n' + arcpy.GetMessages() + '\n'
    arcpy.AddError(msgs)
    print pymsg

finally:
    # Delete in_memory
    arcpy.Delete_management('in_memory')
    arcpy.AddMessage("in_memory intermediate files deleted.")

# End of script
