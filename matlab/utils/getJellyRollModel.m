function model = getJellyRollModel()
%% The first few lines of the runJellyRoll.m example. Utility function for 
% testing grid export.


% Setup mrst modules

mrstModule add ad-core mrst-gui mpfa agmg linearsolvers

%% We setup the geometrical parameters for a 4680 battery. 
%% Those will be gathered in structure spiralparams (see below) and used by SpiralBatteryGenerator to generate the spiral layered geometry of the jelly roll

% Inner radius of the jelly roll
rInner = 2*milli*meter; 

% widths of each component ordered as
% - positive current collector
% - positive electrode
% - electrolyte separator 
% - negative electrode
% - negative current collector

widths = [25, 64, 15, 57, 15]*micro*meter; 

widthDict = containers.Map( ...
    {'ElectrolyteSeparator',... 
     'NegativeActiveMaterial',...
     'NegativeCurrentCollector',...
     'PositiveActiveMaterial',...
     'PositiveCurrentCollector'},...
    widths); 

nwidths = [widthDict('PositiveActiveMaterial');...
           widthDict('PositiveCurrentCollector');...
           widthDict('PositiveActiveMaterial');...
           widthDict('ElectrolyteSeparator');...
           widthDict('NegativeActiveMaterial');...
           widthDict('NegativeCurrentCollector');...
           widthDict('NegativeActiveMaterial');...
           widthDict('ElectrolyteSeparator')]; 

dr = sum(nwidths);

% Outer radius of the jelly roll
rOuter = 46*milli*meter/2;
% Height of the jelly roll
L = 80*milli*meter; 

dR = rOuter - rInner; 
% Computed number of windings
nwindings = ceil(dR/dr);

% number of discretization cells in radial direction for each component.
nrDict = containers.Map( ...
    {'ElectrolyteSeparator',... 
     'NegativeActiveMaterial',...
     'NegativeCurrentCollector',...
     'PositiveActiveMaterial',...
     'PositiveCurrentCollector'},...
    [3, 3, 3, 3, 3]); 

% Number of discretization cells in the angular direction
nas = 10; 

% Number of discretization cells in the longitudonal
nL = 3;

% structure that describes the tab setups (see SpiralBatteryGenerator)
tabparams.tabcase   = 'aligned tabs';
tabparams.width     = 3*milli*meter;
tabparams.fractions = linspace(0.01, 0.9, 6);

testing = false;
if testing
    fprintf('We setup a smaller case for quicker testing\n');
    rOuter = 10*milli*meter/2;
    nL = 2;
end

spiralparams = struct('nwindings'   , nwindings, ...
                      'rInner'      , rInner   , ...
                      'widthDict'   , widthDict, ...
                      'nrDict'      , nrDict   , ...
                      'nas'         , nas      , ...
                      'L'           , L        , ...
                      'nL'          , nL       , ...
                      'tabparams'   , tabparams, ...
                      'angleuniform', true); 

% The input material parameters given in json format are used to populate the paramobj object.
jsonstruct = parseBattmoJson(fullfile('ParameterData','BatteryCellParameters','LithiumIonBatteryCell','lithium_ion_battery_nmc_graphite.json'));

% We define some shorthand names for simplicity.
ne      = 'NegativeElectrode';
pe      = 'PositiveElectrode';
elyte   = 'Electrolyte';
thermal = 'ThermalModel';
am      = 'ActiveMaterial';
itf     = 'Interface';
sd      = 'SolidDiffusion';
ctrl    = 'Control';
cc      = 'CurrentCollector';

jsonstruct.include_current_collectors = true;
jsonstruct.use_thermal = true;

jsonstruct.use_particle_diffusion = true;

diffusionModelType = 'full';

jsonstruct.(pe).(am).diffusionModelType = diffusionModelType;
jsonstruct.(ne).(am).diffusionModelType = diffusionModelType;

paramobj = BatteryInputParams(jsonstruct); 

paramobj.(ne).(am).InterDiffusionCoefficient = 0;
paramobj.(pe).(am).InterDiffusionCoefficient = 0;

% paramobj.(ne).(am).(sd).N = 5;
% paramobj.(pe).(am).(sd).N = 5;

paramobj = paramobj.validateInputParams();


% th = 'ThermalModel';
% paramobj.(th).externalHeatTransferCoefficientSideFaces = 100*watt/meter^2;
% paramobj.(th).externalHeatTransferCoefficientTopFaces = 10*watt/meter^2;

gen = SpiralBatteryGenerator(); 

paramobj = gen.updateBatteryInputParams(paramobj, spiralparams);

model = Battery(paramobj); 