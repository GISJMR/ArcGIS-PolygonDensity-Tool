# -----------------------------------------------
# Name: Polygon Density Tool
# Purpose: Counts the number of overlapping polygons
# Author: James M Roden (based on the model by Dale Honeycutt at ESRI - "Spaghetti and Meatballs")
# Created: Jan 2018
# ArcGIS Version: 10.5
# Python Version 2.6
# PEP8
# -----------------------------------------------

import arcpy
import os
import sys
import traceback


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Polygon Density"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Polygon Density"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameter_0 = arcpy.Parameter(
            displayName='Polygons',
            name='overlap_polygons',
            datatype='GPFeatureLayer',
            parameterType='Required',
            direction='Input')

        parameter_1 = arcpy.Parameter(
            displayName='Output Polygons',
            name='density_polygons',
            datatype='DEFeatureClass',
            parameterType='Required',
            direction='Output')

        parameters = [parameter_0, parameter_1]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        try:

            # ArcGIS environment
            arcpy.env.workspace = "in_memory"
            arcpy.env.scratchWorkspace = "in_memory"
            arcpy.env.overwriteOutput = True

            # ArcGIS Tool Parameters
            overlapping_polygons = parameters[0].valueAsText
            output_polygons = parameters[1].value

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

        except Exception as ex:
            _, error, tb = sys.exc_info()
            traceback_info = traceback.format_tb(tb)[0]
            arcpy.AddError("Error Type: {} \nTraceback: {} \n".format(error, traceback_info))

        finally:
            arcpy.Delete_management('in_memory')
            arcpy.AddMessage("in_memory intermediate files deleted.")
            return
