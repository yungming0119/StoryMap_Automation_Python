from __future__ import annotations
import os

from typing import Callable
from tqdm.auto import tqdm

from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Text, Map, Table, Embed, Scales, TextStyles, Image
from storymap_automation.storymap.inputs import StoryMapVariables
from storymap_automation.ai.demographics_summary import DemographicsSummary
from storymap_automation.ai.func_class_summary import FuncClassSummary
from storymap_automation.ai.traffic_summary import TrafficSummary
from storymap_automation.ai.change_summary import ChangeSummary
from storymap_automation.ai.pavement_summary import PavementSummary
from storymap_automation.ai.greenway_summary import GreenwaySummary
from storymap_automation.ai.crash_summary import CrashSummary
from storymap_automation.ai.landuse_summary import LanduseSummary
import uuid

ProgressCallback = Callable[[str, int, int], None]

def _report(
    callback: ProgressCallback | None,
    message: str,
    completed: int,
    total: int,
) -> None:
    if callback:
        callback(message, completed, total)

def _create_progress_callback(total: int, description: str) -> tuple:
    progress = tqdm(
        total=total,
        desc=description,
        unit="step",
        leave=True,
    )

    def callback(message: str, completed: int, reported_total: int) -> None:
        progress.total = reported_total
        progress.n = completed
        progress.set_postfix_str(message)
        progress.refresh()

        if completed >= reported_total:
            progress.close()

    return progress, callback


def build_story_spec(
    county_name: str,
    overview_text: str,
    gis,
    username: str,
    landuse_image_path: str,
    overview_image_path: str = None,
    pavement_image_path: str = None,
    greenway_image_path: str = None,
    progress_callback: ProgressCallback | None = None,
    **kwargs,
) -> dict:
    """
    Build the StoryMap section dictionary in the same order used by the notebook.
    Each item is either:
      - a Text content object
      - or a 2-item list [content, caption] for maps/tables/embeds
    """
    total = 11
    progress = None

    if progress_callback is None:
        progress, progress_callback = _create_progress_callback(
            total,
            "Building StoryMap",
        )

    try:
        _report(progress_callback, "Starting story map generation", 0, total)

        _report(progress_callback, "Loading county data", 1, total)
        story = StoryMapVariables(gis, username, county_name)

        _report(progress_callback, "Generating functional classification summary", 2, total)
        func_class_summary = FuncClassSummary(story).summary

        _report(progress_callback, "Generating demographics summary", 3, total)
        demographics_summary = DemographicsSummary(
            story,
            progress_callback=progress_callback,
            parent_completed=3,
            parent_total=total
        )

        _report(progress_callback, "Generating current traffic summary", 4, total)
        traffic_summary = TrafficSummary(story.county, story.current_traffic, 2024)

        _report(progress_callback, "Generating forecast traffic summary", 5, total)
        traffic_forecast_summary = TrafficSummary(story.county, story.forecast_traffic, 2045)

        _report(progress_callback, "Generating traffic change summary", 6, total)
        change_summary = ChangeSummary(story.county, story.traffic_change)

        _report(progress_callback, "Generating pavement summary", 7, total)
        pavement_summary = PavementSummary(story.county, story.pavement_condition_summary)

        _report(progress_callback, "Generating greenway summary", 8, total)
        greenway_summary = GreenwaySummary(story.county, story.greenway_and_parks.greenway_summary)

        _report(progress_callback, "Generating crash summary", 9, total)
        crash_summary = CrashSummary(story.county, story.crash_features.crash_summary)

        _report(progress_callback, "Generating landuse summary", 10, total)
        landuse_summary = LanduseSummary(story.county, os.path.abspath(landuse_image_path)).landuse_summary

        _report(progress_callback, "Building story spec", 11, total)
        spec = {
            'summary_title': Text('Summary',style=TextStyles.HEADING),
            'summary_text1': Text(f'This document contains various data resources and an assessment of the major transportation facilities in {story.county} County, Tennessee. The purpose of the document is to give the public, local partners and TDOT a better picture of the existing and projected future conditions on State Routes in {story.county} County. This document includes limited information on locally owned and operated facilities due to a lack of consistently available information relating to their condition, deficiencies, or projected future demand. By examining existing conditions, data trends, projected future conditions and system deficiencies, decision makers and the public at large can use the information for better infrastructure needs decisions, development of plans, grant applications, and prioritization of projects in {story.county} County.', style=TextStyles.PARAGRAPH),
            'summary_text2': Text(f'The data included in the StoryMap is depicted in interactive web maps that contain live data and are updated periodically. It includes a few Dashboards that display interactive data. The document also contains various links to more data resources.',style=TextStyles.PARAGRAPH),
            'summary_text3': Text(f'At the end of the StoryMap document is a list of needs derived from the data resources and from the local stakeholder input.',style=TextStyles.PARAGRAPH),
            # 'overview_image': Image('{overview_image_url}', caption='{overview_image_caption}'),
            # 'county_picture': Image(image_url, caption='{image_caption}'),
            'overview_title': Text(f'Overview of {story.county} County',style=TextStyles.HEADING),
            'overview_text1': Text(f'{story.overview_text1}',style=TextStyles.PARAGRAPH),
            'overview_image': Image(overview_image_path, caption='{overview_image_caption}') if overview_image_path else None,
            'overview_map': [Map(gis.content.get(story.overview_map_id)), f'{story.county} County Overview Map'],
            'demographics_title': Text(f'Demographics',style=TextStyles.HEADING),
            'demographics_text1': Text(f'Key demographic data is displayed in the StoryMap.',style=TextStyles.PARAGRAPH),
            'demographics_text2': Text(f'There are several resources that provide county profiles. The TDOT County Profile Tool: <a href="https://app.powerbigov.us/view?r=eyJrIjoiZDBjZjBkM2MtYWQ3ZC00ZWJjLWJlYTItMzU3YzExYjViYzkzIiwidCI6ImYzNDViZWJmLTBkNzEtNDMzNy05MjgxLTI0Yjk0MTYxNmMzNiJ9">Microsoft Power BI</a> and the <a href="https://comptroller.tn.gov/maps/tennessee-county-profiles.html">Community Profile</a> by the Tennessee Comptroller of the Treasury.',style=TextStyles.PARAGRAPH),
            'demographics_text3': Text(f"The following map contains data on {story.county} County population age groups, sex, ethnicity, poverty, disability, employment and commute from the US Census Bureau's American Community Survey (ACS). Click inside of {story.county} County and click through the different data sets.",style=TextStyles.PARAGRAPH),
            'demographics_map': [Map(gis.content.get(story.demographics_map_id)), f'{story.county} County Overview Map'],
            'demographics_key_facts': Text(f'Demographic Key Facts',style=TextStyles.HEADING2),
            'demographics_facts_text1': Text(f'Demographic key facts are taken from the US Census and compared to the state\'s average. <a href="https://www.census.gov/quickfacts/fact/table/{story.county}countytennessee,TN,US/POP010220">Census Bureau Quick Facts.</a>',style=TextStyles.PARAGRAPH),
            #'age': Text(f'<strong>Age:</strong> The median age in {story.county} County stands at {story.median_age} years, which is much higher than the median age in Tennessee (39.1 years). The most populous age groups are those between {story.age_range[0]} and {story.age_range[1]} years old.',text_style=TextStyles.PARAGRAPH),
            #'education': Text(f'<strong>Education:</strong> In {story.county} County, only {story.education_percent} percent of the population holds a bachelor\'s degree or higher, a figure that is lower compared to the state of Tennessee (31.1%).',text_style=TextStyles.PARAGRAPH),
            #'ethnicty': Text(f'<strong>Ethnicity:</strong> The population in {story.county} County is predominantly of {story.ethnicity} ethnicity ({story.ethnicity_percent}%), with a {story.ethnicity_comparison} percentage than that of Tennessee\'s overall population (72.3%).',text_style=TextStyles.PARAGRAPH),
            #'poverty': Text(f'<strong>Poverty:</strong> Approximately {story.poverty_percent} percent of {story.county} County\'s residents live below the poverty line, a figure that is {story.poverty_comparison} than Tennessee\'s rate of {story.tennessee_poverty_rate} percent. Notably, poverty is more prevalent within the age group of {story.poverty_age[0]} and {story.poverty_age[1]} than any other groups.',text_style=TextStyles.PARAGRAPH),
            #'disability': Text(f'<strong>Disability:</strong> The disability rate in {story.county} County is {story.disability_percent} percent, {story.poverty_comparison} than the state average (10.6%). This rate of disability places unique demands on the transportation system, particularly in terms of public transit.',text_style=TextStyles.PARAGRAPH),
            'age': Text(f'<strong>Age:</strong> {demographics_summary.age_summary}',text_style=TextStyles.PARAGRAPH),
            'education': Text(f'<strong>Education:</strong> {demographics_summary.education_summary}',text_style=TextStyles.PARAGRAPH),
            'ethnicty': Text(f'<strong>Ethnicity:</strong> {demographics_summary.ethnicity_summary}',text_style=TextStyles.PARAGRAPH),
            'poverty': Text(f'<strong>Poverty:</strong> {demographics_summary.poverty_summary}',text_style=TextStyles.PARAGRAPH),
            'disability': Text(f'<strong>Disability:</strong> {demographics_summary.disability_summary}',text_style=TextStyles.PARAGRAPH),
            'employment_title': Text(f'Employment',style=TextStyles.HEADING1),
            'employment_text1': Text(f'The following data is sourced from the Tennessee Department of Labor & Workforce Development - <a href="https://www.tn.gov/workforce/general-resources/major-publications0/major-publications-redirect/public-reports-redirect/labor-force-estimates.html">Labor Force Estimates</a> (Jan. 2026 report). {story.county} County has a labor force of {story.labor_force} and has an unemployment rate of {story.unemployment_rate} percent in {story.county} County. The unemployment rate has seen a {story.unemployment_change} since the 2020 Covid-19 pandemic and is now {story.unemployment_comparison_pre} than pre-pandemic levels.',style=TextStyles.PARAGRAPH),
            'employment_text2': Text(f'The following table lists the largest employers in {story.county} County by employment numbers from <a href="https://tnecd.com/county-profiles/">ECD</a>.',style=TextStyles.PARAGRAPH),
            'employment_table': [Table(df=story.employment_table),f'Top {story.county} County Employers', f'Top {story.county} County Employers'],
            'commute_title': Text(f'Commute',style=TextStyles.HEADING1),
            'commute_text1': Text(f'The majority of commuters from {story.county} County commute outside of the {story.commute_to[0]} to {story.commute_to[1]} ({story.commute_to_count[1]} commuters) and {story.commute_to[2]} County ({story.commute_to_count[2]} commuters). {story.county} County receives the largest number of commuters from {story.commute_from[0]} County, followed by {story.commute_from[1]} County.'),
            'commute_text2': Text(f'Commute data for Tennessee is sourced from the Tennessee Department of Labor and Workforce Development (2022): <a href="https://data.tn.gov/t/Public/views/commuter/County_Dash?iframeSizedToWindow=true&%3Aembed=y&%3AshowAppBanner=false&%3Adisplay_count=no&%3AshowVizHome=no&%3Atoolbar=no&%3Atabs%20=no">Commuter Data County</a>.',style=TextStyles.PARAGRAPH),
            'commute_table': [Table(df=story.commute_table),f'Commuters to and from {story.county} County to Neighboring Counties'],
            'population_forecast_title': Text(f'Population Forecast',style=TextStyles.HEADING1),
            'population_forecast_text1': Text(story.trend_text,style=TextStyles.PARAGRAPH),
            #'population_forecast_text1': Text(f'The population in {story.county} County is forecasted to {story.population_forecast_change} between now and 2070: <a href="https://myutk.maps.arcgis.com/apps/dashboards/e394a78a6c754af7b6da1a771acc3b26#">Population Projection 2022-2070</a>',style=TextStyles.PARAGRAPH),
            'population_forecast_map': [Map(gis.content.get(story.population_forecast_map_id)),f'{story.county} County 2045 Population Forecast'],
            'land_use_title': Text(f'Land Use',style=TextStyles.HEADING1),
            # 'land_use_text1': Text(f'',style=TextStyles.PARAGRAPH),
            # 'land_use_image': Image(landuse_image_path, caption=f'') if landuse_image_path else None,
            'land_use_text': Text(landuse_summary,style=TextStyles.PARAGRAPH),
            'land_use_map': [Map(gis.content.get(story.land_use_map_id)), f'{story.county} County Land Use Map'],
            'roadway_network_title': Text(f'Roadway Network',style=TextStyles.HEADING1),
            'roadway_text1': Text(f'Roadway network information is displayed on the map. By clicking on a roadway, it will display information on roadway geometrics and traffic.',style=TextStyles.PARAGRAPH),
            'roadway_map': [Map(gis.content.get(story.roadway_map_id)), f'{story.county} County Roadway Network'],
            'functioal_classification_title': Text(f'Functional Classification',style=TextStyles.HEADING1),
            'functioal_classification_text1': Text(f'The functional classification system is displayed on the map. Data on functionally classified roads is displayed in the TDOT Dashboard, shown further below.',style=TextStyles.PARAGRAPH),
            'functional_classification_map': [Map(gis.content.get(story.functional_classification_map_id)), f'{story.county} County Functional Classification Map'],
            'functioal_classification_text2': Text(f'{func_class_summary}',style=TextStyles.PARAGRAPH),
            # 'funcational_classification_text3': Text(f'The Functional Classification of roadways is indicated in this TDOT Functional Classification Dashboard. Select \"{story.county} County\" and it will display the functional classes of {story.county} County\'s roads as well as the road mileage per functional class. There are {story.other_principal_arterials_miles} miles of Other Principal Arterials, {story.rural_minor_collectors_miles} miles of Rural Minor Collectors, {story.rural_minor_arterials_miles} miles of Rural Minor Arterials, {story.rural_major_collectors_miles} Rural Major Collectors, and {story.rural_local_roads_miles} miles of Rural Local Roads.',style=TextStyles.PARAGRAPH),
            'functoinal_classification_dashboard': [Embed("https://myutk.maps.arcgis.com/apps/dashboards/0901655139694144a16f7812a52b4f36",caption=f'TDOT Functional Classification Dashboard'),f'TDOT Functional Classification Dashboard'],
            'bridge_condition_title': Text(f'Bridge Condition',style=TextStyles.HEADING1),
            'bridge_condition_text1': Text(f'{story.county} County has {story.bridge_count} bridges. Based on the <a href="https://infobridge.fhwa.dot.gov/">National Bridge Inventory</a> there are {story.good_condition_bridges} bridges in {story.county} County in "good" condition, {story.fair_condition_bridges} in "fair" condition, and {story.poor_condition_bridges} bridges in "poor" condition.',style=TextStyles.PARAGRAPH),
            'poor_bridge_table': [Table(df=story.bridge_table),f'Bridges rated "Poor" in {story.county} County (Source: National Bridge Inventory)'],
            'bridge_condition_map': [Map(gis.content.get(story.bridge_condition_map_id)),f'{story.county} County Bridge Condition'],
            'state_aid_road_title': Text(f'State-Aid Roads',style=TextStyles.HEADING1),
            'state_aid_road_text1': Text(f'The State Aid program provides funds to county governments for the improvement or rehabilitation of roads on the State-Aid system. The State-Aid system is a network of local selected county roads that require construction, planning, or paving projects. The Roadway Data office is responsible for processing county requests for additions or deletions of qualifying roads to the State-Aid System.', style=TextStyles.PARAGRAPH),
            'state_aid_road_map': [Map(gis.content.get(story.state_aid_road_map_id)),f'{story.county} County State-Aid Roads'],
            'state_aid_road_text2': Text(f'The process involves the submission of documents to the Roadway Data Office through a designated TDOT Region State-Aid office. There is also collaboration between the State-Aid Engineer and personnel from the Region Office.', style=TextStyles.PARAGRAPH),
            'state_aid_road_text3': Text(f'TDOT has a State-Aid Dashboard with up-to-date information on the current state-aid roads. {story.county} County needs to be selected to look up the data. In the interactive TDOT Dashboard, State-Aid Roads are displayed as well. Select "{story.county} County" as the county and data on State-Aid Roads will be shown. ', style=TextStyles.PARAGRAPH),
            'state_aid_road_text4': Text(f'There are {story.state_aid_count} State-Aid Routes in {story.county} County, which equals {story.state_aid_miles:.2f} miles.', style=TextStyles.PARAGRAPH),
            'state_aid_road_dashboard': [Embed("https://myutk.maps.arcgis.com/apps/dashboards/fd3e077870ce4dd9a1722d9b69e099f2#",caption='TDOT State-Aid Roads Dashboard for {story.county} County'),f'TDOT State-Aid Roads Dashboard for {story.county} County'],
            'traffic_volume_title': Text(f'Traffic Volume',style=TextStyles.HEADING1),
            'tennessee_travel_demand_model_title': Text(f'Tennessee Travel Demand Model',style=TextStyles.HEADING2),
            'tn_travel_demand_model_text1': Text(f'The Tennessee Statewide Travel Demand Model (TSM) version 4.0 produces traffic forecasts for the years 2025, 2035, and 2045. Modeled traffic is projected from traffic counts for the base year 2018. Future changes in traffic are determined using estimated future population, employment, and household numbers. Changes to the road network through construction and improvement projects also impact forecasted traffic.',style=TextStyles.PARAGRAPH),
            'tn_travel_demand_model_text2': Text(f'The TSM Dashboard is an interface in which users can explore and interact with some of the most valuable input and output data for the model. Where people live, where they work, and the roads they use to get from place to place are all integral to identifying the traffic patterns of today and the future.',style=TextStyles.PARAGRAPH),
            'tn_travel_demand_model_text3': Text(f'The TSM Dashboard provides data on population, household density, employment, vehicle miles traveled (VMT), volume/capacity (v/c) ratio, traffic volumes (AADT) for cars and trucks for the base year 2018, and forecast years 2025, 2035, 2045.  ',style=TextStyles.PARAGRAPH),
            'tsm_dashboard': [Embed("https://myutk.maps.arcgis.com/apps/dashboards/90141e180b874104a97e8750f33f81f8",caption='TSM Network Dashboard'),f'TSM Network Dashboard'],
            'current_traffic_volume_title': Text(f'Current Traffic Volume',style=TextStyles.HEADING2),
            #'current_traffic_volume_text1': Text(f'{story.dominant_routes} carry the dominant share of the traffic volumes in {story.county} County. The highest traffic volumes are on {story.dominant_route}, the predominant {story.dominant_direction} route. Secondary routes regarding traffic volumes are {story.secondary_routes}.',style=TextStyles.PARAGRAPH),
            'current_traffic_volume_text1': Text(traffic_summary.aadt_summary,style=TextStyles.PARAGRAPH),
            'traffic_volume_map': [Map(gis.content.get(story.traffic_volume_map_id)), f'{story.county} County 2024 Traffic'],
            'forecasted_traffic_volume_title': Text(f'Forecasted Traffic Volume',style=TextStyles.HEADING2),
            # 'forecasted_traffic_volume_text1': Text(f'Traffic volumes are forecasted to {story.forecasted_increase} in 2045 on the roadway system in {story.county} County. The highest volumes are on {story.forecasted_routes}.',style=TextStyles.PARAGRAPH),
            'forecasted_traffic_volume_text1': Text(traffic_forecast_summary.aadt_summary,style=TextStyles.PARAGRAPH),
            'forecasted_traffic_volume_map': [Map(gis.content.get(story.forecasted_traffic_volume_map_id)), f'{story.county} County 2045 Traffic Flow'],
            'traffic_changes_title': Text(f'Traffic Changes 2018-2045',style=TextStyles.HEADING2),
            'traffice_changes_text1': Text(change_summary.aadt_change_summary,style=TextStyles.PARAGRAPH),
            # 'traffic_changes_text1': Text(f'The steepest traffic increases are on sections of {story.traffic_changes_routes}.',style=TextStyles.PARAGRAPH),
            # 'traffic_changes_text2': Text(f'{story.traffic_decrease_route} is forecasted to experience a traffic decrease between 2018 and 2045, while traffic increases on {story.traffic_increase_route}.', style=TextStyles.PARAGRAPH),
            'traffic_changes_am_map': [Map(gis.content.get(story.traffic_changes_am_map_id)), f'{story.county} County Total AM Flow Change 2018-2045'],
            'traffic_changes_pm_map': [Map(gis.content.get(story.traffic_changes_pm_map_id)), f'{story.county} County Total PM Flow Change 2018-2045'],
            'truck_volume_title': Text(f'Truck Volume',style=TextStyles.HEADING1),
            'current_truck_volume_title': Text(f'Current Truck Volume (Base Year 2018)',style=TextStyles.HEADING2),
            'current_truck_volume_text1': Text(f'The map shows 2018 modeled multi-unit truck traffic across {story.county} County.',style=TextStyles.PARAGRAPH),
            'current_truck_volume_text2': Text(traffic_summary.truck_aadt_summary,style=TextStyles.PARAGRAPH),
            # 'current_truck_volume_text2': Text(f'The highest truck volumes are on {story.dominant_truck_routes}.',style=TextStyles.PARAGRAPH),
            'current_truck_volume_map': [Map(gis.content.get(story.current_truck_volume_map_id)), f'{story.county} County 2018 Base Year Truck Volumes'],
            'truck_volume_forecast_title': Text(f'Forecasted Truck Volume 2045',style=TextStyles.HEADING2),
            # 'truck_volume_forecast_text1': Text(f'Overall, truck traffic is predicted to {story.forecasted_truck_increase} in the forecast year of 2045. The primary freight route, {story.primary_freight_route}, is forecasted to have the highest traffic volumes.',style=TextStyles.PARAGRAPH),
            'truck_volume_forecast_text1': Text(traffic_forecast_summary.truck_aadt_summary,style=TextStyles.PARAGRAPH),
            'truck_volume_forecast_map': [Map(gis.content.get(story.truck_volume_forecast_map_id)), f'{story.county} County Truck Volumes 2045 Forecast'],
            'truck_flow_changes_title': Text(f'Truck Flow Changes 2018-2045',style=TextStyles.HEADING2),
            'truck_flow_changes_text1': Text(change_summary.truck_aadt_change_summary,style=TextStyles.PARAGRAPH),
            # 'truck_flow_changes_text1': Text(f'The map indicates that truck traffic is becoming increasingly concentrated on {story.primary_freight_route}, which is the county\'s primary {story.primary_freight_direction} freight corridor. The strongest positive truck-flow changes occur along this corridor as it passes through the {story.primary_freight_area}.',style=TextStyles.PARAGRAPH),
            'truck_flow_changes_map': [Map(gis.content.get(story.truck_flow_changes_map_id)), f'{story.county} County Truck Flow Changes 2018-2045'],
            'vehicle_miles_traveled_title': Text(f'Vehicle Miles Traveled (VMT)',style=TextStyles.HEADING1),
            'vehicle_miles_traveled_text1': Text(f'Vehicle Miles Traveled (VMT) measures the amount and distance traveled. Average daily traffic (AADT) is multiplied by the length of the road segment. It measures demand for vehicle travel.',style=TextStyles.PARAGRAPH),
            'vehicle_miles_traveled_base_year_title': Text(f'Vehicle Miles Traveled (VMT) 2018 Base Year',style=TextStyles.HEADING2),
            'vehicle_miles_traveled_base_year_text1': Text(f'The map shows the 2018 base year VMT for {story.county} County.',style=TextStyles.PARAGRAPH),
            'vehicle_miles_traveled_base_year_text2': Text(traffic_summary.vmt_summary,style=TextStyles.PARAGRAPH),
            'vehicle_miles_traveled_base_year_map': [Map(gis.content.get(story.vehicle_miles_traveled_base_year_map_id)), f'{story.county} County Vehicle Miles Traveled (VMT) 2018 Base Year'],
            'vehicle_miles_traveled_forecast_title': Text(f'Vehicle Miles Traveled (VMT) 2045 Forecast',style=TextStyles.HEADING2),
            'vehicle_miles_traveled_forecast_text1': Text(f'The map shows the 2045 forecasted VMT for {story.county} County.',style=TextStyles.PARAGRAPH),
            'vehicle_miles_traveled_forecast_text2': Text(traffic_forecast_summary.vmt_summary,style=TextStyles.PARAGRAPH),
            'vehicle_miles_traveled_forecast_map': [Map(gis.content.get(story.vehicle_miles_traveled_forecast_map_id)), f'{story.county} County Vehicle Miles Traveled (VMT) 2045 Forecast'],
            'vmt_changes_title': Text(f'Vehicle Miles Traveled (VMT) Changes 2018-2045',style=TextStyles.HEADING2),
            'vmt_changes_text1': Text(change_summary.vmt_change_summary,style=TextStyles.PARAGRAPH),
            # 'vmt_changes_text1': Text(f'The map shows the changes in VMT between 2018 and 2045 for {story.county} County. The highest VMT changes are on {story.highest_vmt_changes_route}.',style=TextStyles.PARAGRAPH),
            'vmt_changes_map': [Map(gis.content.get(story.vmt_changes_map_id)), f'{story.county} County Vehicle Miles Traveled (VMT) Changes 2018-2045'],
            'volume_capacity_ratio_title': Text(f'Volume/Capacity (V/C) Ratio',style=TextStyles.HEADING1),
            'volume_capacity_ratio_text1': Text(f'The volume/capacity (v/c) ratio is an indicator for congestion. If the v/c ratio is above 1 it indicates congestion. The following sections show v/c ratio levels in the base year 2018 and forecast year 2045.',style=TextStyles.PARAGRAPH),
            'vc_ratio_base_year_title': Text(f'Volume/Capacity Ratio 2018 Base Year',style=TextStyles.HEADING2),
            'vc_ratio_base_year_text1': Text(f'The map shows the 2018 base year v/c ratio for {story.county} County. The highest v/c ratio is on {story.highest_vc_ratio_route}.',style=TextStyles.PARAGRAPH),
            'vc_ratio_base_year_am_map': [Map(gis.content.get(story.vc_ratio_base_year_am_map_id)), f'{story.county} County 2018 AM VC Ratio'],
            'vc_ratio_base_year_pm_map': [Map(gis.content.get(story.vc_ratio_base_year_pm_map_id)), f'{story.county} County 2018 PM VC Ratio'],
            'vc_ratio_forecast_title': Text(f'Volume/Capacity Ratio 2045 Forecast',style=TextStyles.HEADING2),
            'vc_ratio_forecast_text1': Text(f'The map shows the 2045 forecasted v/c ratio for {story.county} County. The highest v/c ratio is on {story.highest_vc_ratio_forecast_route}.',style=TextStyles.PARAGRAPH),
            'vc_ratio_forecast_am_map': [Map(gis.content.get(story.vc_ratio_forecast_am_map_id)), f'{story.county} County 2045 AM VC Ratio'],
            'vc_ratio_forecast_pm_map': [Map(gis.content.get(story.vc_ratio_forecast_pm_map_id)), f'{story.county} County 2045 PM VC Ratio'],
            'uniform_traffic_control_delay_title': Text(f'Uniform Traffic Control Delay (UTCD)',style=TextStyles.HEADING1),
            'uniform_traffic_control_delay_text1': Text(f'Uniform traffic control delay times indicate delays at signalized intersections.',style=TextStyles.PARAGRAPH),
            'uniform_traffic_control_delay_map': [Map(gis.content.get(story.uniform_traffic_control_delay_map_id)), f'{story.county} County Forecast 2045 AB Delay'],
            'pavement_conditions_title': Text(f'Pavement Conditions',style=TextStyles.HEADING1),
            'pavement_conditions_text1': Text(f'Pavement conditions are determined by the Pavement Quality Index (PQI). {story.county}\'s pavement conditions are located in TDOT\'s <a href="https://www.tn.gov/tdot/pm/programs/pavement-program.html">2026-2028-Year Pavement Program</a>.',style=TextStyles.PARAGRAPH),
            'pavement_coditions_text2': Text(pavement_summary.pavement_summary,style=TextStyles.PARAGRAPH),
            'pavement_conditions_text3': Text(f'{story.pavement_condition_list}',style=TextStyles.BULLETLIST),
            'pavement_conditions_map': [Map(gis.content.get(story.pavement_conditions_map_id)), f'{story.county} County Pavement Roughness'],
            'greenway_and_parks_title': Text(f'Greenways and Parks',style=TextStyles.HEADING1),
            'greenway_and_parks_text1': Text(greenway_summary.greenway_summary,style=TextStyles.PARAGRAPH),
            'greenway_and_parks_text2': Text(f'There are {story.parks_count} parks in {story.county} County. The <a href="https://experience.arcgis.com/experience/0ef2687be56940408d73ced2dfc170b6/">TREC (Trails - Recreation - Environment - Community) Project Map</a> contains data on paved trails, hiking paths, horseback riding and recreation areas. The map is easily accessible online.',style=TextStyles.PARAGRAPH),
            'greenway_and_parks_embed': [Embed('https://experience.arcgis.com/experience/0ef2687be56940408d73ced2dfc170b6',caption='TREC (Trails - Recreation - Environment - Community) Project Map'),f'TN TREC Project Map'],
            'trails_and_parks_map': [Map(gis.content.get(story.trails_and_parks_map_id)), f'{story.county} County TREC Trails and Parks'],
            'sidewalks_title': Text(f'Sidewalks',style=TextStyles.HEADING1),
            'sidewalks_text1': Text(f'There are sidewalks with the total of {story.sidewalks_miles:.2f} miles in {story.county} County.',style=TextStyles.PARAGRAPH),
            'sidewalks_map': [Map(gis.content.get(story.sidewalks_map_id)), f'{story.county} County Sidewalks'],
            'bicycle_ways_title': Text(f'Bicycle Ways',style=TextStyles.HEADING1),
            'bicycle_ways_text1': Text(f'There are {story.bicycle_ways_miles:.2f} of bicycle ways in {story.county} County.',style=TextStyles.PARAGRAPH),
            'proposed_tennessee_designated_bicycle_routes_title': Text(f'Proposed Tennessee Designated Bicycle Routes',style=TextStyles.HEADING2),
            'proposed_tennessee_designated_bicycle_routes_text1': Text(f'The map shows the proposed Tennessee designated bicycle routes in {story.county} County.',style=TextStyles.PARAGRAPH),
            'proposed_tennessee_designated_bicycle_routes_map': [Map(gis.content.get(story.proposed_tennessee_designated_bicycle_routes_map_id)), f'{story.county} County Proposed State Bicycle Routes'],
            'bicycle_level_of_service_title': Text(f'Bicycle Level of Service',style=TextStyles.HEADING1),
            'bicycle_level_of_service_text1': Text(f'Tennessee\'s state and federal highways are rated for bicycle suitability using Bicycle Level of Service (BLOS). The inputs for calculating BLOS are flow rate, effective width of road segment, and the effective speed factor (data from ETRIMS). The result is an overall score about on-road bicyclist comfort level as a function of a roadway\'s geometry and traffic conditions. The score also depends on the percentage of heavy vehicles and on the pavement surface rating. The score resulting from the BLOS equation is converted into a LOS A through F. With A being very suitable and F not suitable.',style=TextStyles.PARAGRAPH),
            'bicycle_corridors_text': Text(f'Best bike-route corridors in {story.county} County:', style=TextStyles.PARAGRAPH),
            'bicycle_corridors_list': Text(f'<li>{story.bicycle_corridors[0]}</li><li>{story.bicycle_corridors[1]}</li><li>{story.bicycle_corridors[2]}</li>', style=TextStyles.BULLETLIST),
            'bicycle_level_of_service_map': [Map(gis.content.get(story.bicycle_level_of_service_map_id)), f'{story.county} County Bicycle Level of Service'],
            'public_transit_title': Text(f'Public Transit',style=TextStyles.HEADING1),
            'public_transit_text1': Text(f'Public transit services in {story.county} County are provided by {story.public_transit_provider}. It provides curb-to-curb public transportation services to all residents {story.public_transit_coverage}. The program offers transportation to facilities, shopping, and doctors. Anybody can participate in public transportation.',style=TextStyles.PARAGRAPH),
            'public_transit_text2': Text(f'The number of trips increased by {story.public_transit_increase} percent from 2024 to 2025. The number of trips for {story.public_transit_service} increased by a lot from 2024 to 2025.',style=TextStyles.PARAGRAPH),
            'trip_by_purpose_table': [Table(df=story.purpose_table),f'UCHRA Public Transportation Annual Trips by Purpose in {story.county} County'],
            'TDOT_project_title': Text(f'TDOT Projects',style=TextStyles.HEADING1),
            'TDOT_project_text1': Text(f'<a href="https://www.tn.gov/tdot/build-with-us.html">TDOT\'s 10-Year Plan</a> is fiscally constrained. It delivers TDOT\'s current 3-Year Plan as a priority and accelerates IMPROVE Act projects. It also provides important funding for collaboration with communities, such as the Statewide Partnership Program (SPP), and investments in sidewalks and bikeways through grants and other initiatives.',style=TextStyles.PARAGRAPH),
            'tdot_project_text2': Text(f'There is {story.project_number} proposed for {story.county} County in the TDOT 10-Year Plan. The PE Design Year is {story.pe_design_year}, ROW Year is {story.row_year}, and Estimated Construction Year is {story.estimated_construction_year}. The estimated cost is ${story.estimated_cost} million.',style=TextStyles.PARAGRAPH),
            'vehicle_crash_title': Text(f'Vehicle Crashes',style=TextStyles.HEADING1),
            'vehicle_crash_text1': Text(f'There was a total of {story.total_crashes} vehicle crashes in {story.county} County.',style=TextStyles.PARAGRAPH),
            'vehicle_crash_text2': Text(crash_summary.crash_summary,style=TextStyles.PARAGRAPH),
            'crash_density_title': Text(f'Crash Density (2021-2024)',style=TextStyles.HEADING2),
            'crash_density_text1': Text(f'The map shows the crash density in {story.county} County between 2021 and 2024. The highest crash density is on {story.highest_crash_density_route}.',style=TextStyles.PARAGRAPH),
            'crash_density_text2': Text(f'Various Crash <a href="https://www.tn.gov/content/tn/safety/stats/dashboards.html">Dashboards</a> are available from the Department of Safety and Homeland Security.',style=TextStyles.PARAGRAPH),
            'crash_density_map': [Map(gis.content.get(story.crash_density_map_id)),f'{story.county} County Crash Density'],
            'bicycle_and_pedestrian_crash_title': Text(f'Bicycle and Pedestrian Crashes',style=TextStyles.HEADING1),
            'bicycle_and_pedestrian_crash_text1': Text(f'There were a total of {story.total_bicycle_crashes} bicycle crashes and {story.total_pedestrian_crashes} pedestrian crashes in {story.county} County.',style=TextStyles.PARAGRAPH),
            'bicycle_and_pedestrian_crash_map': [Map(gis.content.get(story.bicycle_and_pedestrian_crash_map_id)),f'{story.county} County Bicycle and Pedestrian Crashes (2021-2025)'],
            'funding_sources_title': Text(f'Funding Sources',style=TextStyles.HEADING1),
            'funding_sources_text1': Text(f'There are various funding sources available in form of grants and programs. The best tool for communities and planners to use is the TDOT Transportation Funding Database.',style=TextStyles.PARAGRAPH),
            'transportation_funding_database_title': Text(f'TDOT Transportation Funding Database',style=TextStyles.HEADING2),
            'transportation_funding_database_text1': Text(f'This Transportation Funding Database identifies federal, state, non-profit funding opportunities. Use the tools: "category, general search, agency" to search for grants.',style=TextStyles.PARAGRAPH),
            'transportation_funding_database_embed': [Embed('https://app.powerbigov.us/view?r=eyJrIjoiMTg5MDM4MzgtMjNjNi00ZTE1LWI3ODktYjJhOWI0ZjQxMjE2IiwidCI6ImYzNDViZWJmLTBkNzEtNDMzNy05MjgxLTI0Yjk0MTYxNmMzNiJ9'),f'UCHRA Public Transportation Annual Trips by Purpose in {story.county} County'],
            'statewide_partnership_program_title': Text(f'Statewide Partnership Program (SPP)',style=TextStyles.HEADING2),
            'statewide_partnership_program_text1': Text(f'As part of TDOT\'s 10-Year Project Planning process, the Statewide Partnership Program (SPP) is a critical avenue for local stakeholders to provide input on their priorities to better inform the annual reassessment of TDOT\'s 10-Year Project Plan. The program supports local authorities in maximizing funding dollar for critical local mobility and economic development needs. Local jurisdictions, municipalities, and counties can submit projects.',style=TextStyles.PARAGRAPH),
            'eligible_projects_text1': Text(f'<strong>Eligible projects:</strong>',style=TextStyles.PARAGRAPH),
            'eligible_projects_list': Text(f'<li>Highway Capacity (e.g. lane addition, roadway extension)</li><li>Highway ITS/system operations (e.g. technology upgrades, operation)</li><li>Highway safety (e.g. roadway geometric, design, or operation improvements targeted to a safety need)</li><li>Major bridge project (e.g. replacement or reconstruction)</li><li>Major pavement project (e.g. rehab or reconstruction)</li><li>Projects currently included in an MPO TIP for funding consideration are encouraged. The MPO TIP would be listed as the source for committed funding.</li>',style=TextStyles.BULLETLIST),
            'county_stakeholder_survey_title': Text(f'County Stakeholder Survey',style=TextStyles.HEADING1),
            'county_stakeholder_survey_text1': Text(f'A survey to receive stakeholder feedback was send out in May 2025',style=TextStyles.PARAGRAPH),
            'county_stakeholder_survey_text2': Text(f'The list of stakeholders in {story.county} County who received the survey included: mayors of county and cities, Planning Commission members, public transit providers (e.g. Development District\'s Human Resource Agency), roadway superintendents, police and fire chiefs, school superintendents, etc.',style=TextStyles.PARAGRAPH),
            'county_stakeholder_survey_text3': Text(f'The survey had three parts, 1) A ranking of Transportation Planning Priorities, 2) The question "What is the biggest concern of the transportation network in {story.county} County?", 3) An interactive map on which stakeholders were asked to drop pins identifying transportation issues. The categories are defined here.',style=TextStyles.PARAGRAPH),
            'county_stakeholder_survey_table': [Table(df=story.stake_table),f'TDOT Transportation Funding Database'],
            'county_stakegholder_survey_text4': Text(f'The map below shows the identified locations by category and by clicking on the dots, the comments by the stakeholders can be opened. Most of the comments were on roadway needs.',style=TextStyles.PARAGRAPH),
            'county_stakeholder_survey_map': [Map(gis.content.get(story.county_stakeholder_survey_map_id)),f'{story.county} County Stakeholder Survey Map'],
            'county_stakeholder_survey_text5': Text(f'In the stakeholder survey the question was asked what the biggest issue of the {story.county} County transportation system was {story.issue}. The predominant answer was {story.answer} as the biggest problem.',style=TextStyles.PARAGRAPH),
            'county_stakeholder_survey_text6': Text(f'The stakeholder input was important to identify any perceived transportation needs and issues of {story.county} County\'s transportation system. The top priority is {story.priority}.',style=TextStyles.PARAGRAPH),
            'need_list_summary_title': Text(f'Summary of Needs',style=TextStyles.HEADING1),
            'need_list_summary_text1': Text(f'The following list is a summary of needs for {story.county} County derived from the data and stakeholder input. This list can be used for planning future transportation investments and grant applications, and strategizing project priorities.',style=TextStyles.PARAGRAPH),
            'roadway_maintenance_needs_table': [Table(df=story.roadway_maintenance_needs_table),f'Roadway Maintenance Needs in {story.county} County'],
            'signage_and_traffic_control_measures_needs_table': [Table(df=story.signage_and_traffic_control_measures_needs_table),f'Signage and Traffic Control Measures Needs in {story.county} County'],
            'roadway_improvements_needs_table': [Table(df=story.roadway_improvements_needs_table),f'Roadway Improvements Needs in {story.county} County'],
            # 'traffic_needs_table': [Table(df=story.traffic_needs_table),f'Traffic Needs in {story.county} County'],
            'VMT_needs_table': [Table(df=story.vmt_needs_table),f'Vehicle Miles Traveled (VMT) Needs in {story.county} County'],
            'crashes_table': [Table(df=story.crashes_table),f'Crashes Needs in {story.county} County'],
            'sidewalks_needs_table': [Table(df=story.sidewalks_needs_table),f'Sidewalks Needs in {story.county} County'],
            'demographics_needs_table': [Table(df=story.demographics_needs_table),f'Demographics Needs in {story.county} County'],
            'communication_needs_table': [Table(df=story.communication_needs_table),f'Communication Needs in {story.county} County']
        }
        _report(progress_callback, "Completed story map generation", 11, total)

        return spec
    finally:
        if progress is not None:
            progress.close()

    
def render_story_map(
    gis,
    story_spec,
    county=None,
    id=None,
    img_url=None,
    progress_callback: ProgressCallback | None = None,
) -> StoryMap:
    """
    Render the ordered section dictionary into a StoryMap in the same way the notebook does.
    """
    if id:
        story_map = StoryMap(id, gis=gis)
    else:
        story_map = StoryMap(gis=gis)
    total =len(story_spec)
    progress = None

    if progress_callback is None:
        progress, progress_callback = _create_progress_callback(
            total,
            "Rendering StoryMap",
        )
    try:
        _report(progress_callback, "Rendering StoryMap", 0, total)
        for completed, section in enumerate(story_spec, start=1):
            content = story_spec[section]
            if content is None:
                _report(progress_callback, f"Skipped {section}", completed, total)
                continue

            if isinstance(content, list):
                if not content or content[0] is None:
                    raise ValueError(f"Story section '{section}' has no content")

                story_map.add(content[0], caption=content[1])
                if isinstance(content[0], Map):
                    map_content = content[0]
                    extent = map_content.map.extent
                    map_content.set_viewpoint(
                        {
                            "xmin": extent[0][0],
                            "ymin": extent[0][1],
                            "xmax": extent[1][0],
                            "ymax": extent[1][1],
                        },
                        Scales.METROPOLITAN
                    )
                    map_content.show_legend = True
                    map_content.legend_pinned = True

                    
                if isinstance(content[0], Embed):
                    content[0].display = "inline"
                    content[0].caption = content[1]
            else:
                story_map.add(content)
            _report(progress_callback, f"Added {section}", completed, total)

        cover = story_map.contents[0]
        cover.title = f'{county} County Story Map'
        cover.type='sidebyside'
        cover_image = Image(os.path.abspath(img_url)) if img_url else None
        cover.media = cover_image
        cover.summary = f'Comprehensive Assessment and Resource Guidance of {county} County'
        story_map.contents[1].hidden = False
        return story_map
    finally:
        if progress is not None:
            progress.close()




def save_story_map(story_map, county_name: str, gis, *, title=None, img_url=None):
    """
    Save the StoryMap to ArcGIS with a clean title.
    """
    username = gis.users.me.username.split('_')[0]
    item = story_map.save(
        title=title or f"{county_name} County Transportation Story Map__{username}_{uuid.uuid4().hex}",
        tags=[f"{county_name} County", "Transportation", "Story Map"],
    )
    item.update(item_properties={
        "description": f"This document contains various data resources and an assessment of the major transportation facilities in {county_name} County, Tennessee. The purpose of the document is to give the public, local partners and TDOT a better picture of the existing and projected future conditions on State Routes in {county_name} County. This document includes limited information on locally owned and operated facilities due to a lack of consistently available information relating to their condition, deficiencies, or projected future demand. By examining existing conditions, data trends, projected future conditions and system deficiencies, decision makers and the public at large can use the information for better infrastructure needs decisions, development of plans, grant applications, and prioritization of projects in {county_name} County.",
        "snippet": f"Comprehensive Assessment and Resource Guidance of {county_name} County",
        "access": "private",
        "publish": True
    })
    if img_url:
        img_url = os.path.abspath(img_url)
        if os.path.exists(img_url):

            item.update_thumbnail(file_path=img_url)