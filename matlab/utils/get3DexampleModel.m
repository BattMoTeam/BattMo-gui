function model = get3DexampleModel()

%% Pseudo-Four-Dimensional (P4D) Lithium-Ion Battery Model
% This example demonstrates how to setup a P4D model of a Li-ion battery
% and run a simple simulation.

% Clear the workspace and close open figures
% clear all
% close all
% clc

%% Import the required modules from MRST
% load MRST modules
mrstModule add ad-core mrst-gui mpfa

%% Setup the properties of Li-ion battery materials and cell design
% The properties and parameters of the battery cell, including the
% architecture and materials, are set using an instance of
% :class:`BatteryInputParams <Battery.BatteryInputParams>`. This class is
% used to initialize the simulation and it propagates all the parameters
% throughout the submodels. The input parameters can be set manually or
% provided in json format. All the parameters for the model are stored in
% the paramobj object.
jsonstruct = parseBattmoJson(fullfile('ParameterData','BatteryCellParameters','LithiumIonBatteryCell','lithium_ion_battery_nmc_graphite.json'));
jsonstruct.include_current_collectors = true;

paramobj = BatteryInputParams(jsonstruct);

% We define some shorthand names for simplicity.
ne      = 'NegativeElectrode';
pe      = 'PositiveElectrode';
am      = 'ActiveMaterial';
cc      = 'CurrentCollector';
elyte   = 'Electrolyte';
thermal = 'ThermalModel';
ctrl    = 'Control';

%% Setup the geometry and computational mesh
% Here, we setup the 3D computational mesh that will be used for the
% simulation. The required discretization parameters are already included
% in the class BatteryGenerator3D.
gen = BatteryGenerator3D();

% Now, we update the paramobj with the properties of the mesh.
paramobj = gen.updateBatteryInputParams(paramobj);

%%  Initialize the battery model. 
% The battery model is initialized by sending paramobj to the Battery class
% constructor. see :class:`Battery <Battery.Battery>`.
model = Battery(paramobj);