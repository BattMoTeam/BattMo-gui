function result = runEncodedJsonStruct()
    jsonfilename = fullfile('battmo_formatted_input.json');
    jsonstruct = parseBattmoJson(jsonfilename);
    jsonstruct.Geometry.case = jsonstruct.Geometry.xCase;
    % jsonstruct.Geometry.case doesn't exist (why??), instead there's xCase

    % Run battery simulation with function that takes json input
    output = runBatteryJson(jsonstruct);


    % shorthands
    ne      = 'NegativeElectrode';
    pe      = 'PositiveElectrode';
    am      = 'ActiveMaterial';
    cc      = 'CurrentCollector';
    elyte   = 'Electrolyte';
    thermal = 'ThermalModel';
    ctrl    = 'Control';
    sd      = 'SolidDiffusion';

    states = output.states;

    cell_voltage = cellfun(@(x) x.Control.E, states);
    cell_current = cellfun(@(x) x.Control.I, states);
    time = cellfun(@(x) x.time, states);
    time_values = time/hour;

    number_of_states = length(states);

    negative_electrode_grid = output.model.(ne).(am).G;
    electrolyte_grid = output.model.(elyte).G;
    positive_electrode_grid = output.model.(pe).(am).G;


    % Negative Electrode Concentration
    negative_electrode_concentration = cell(number_of_states, negative_electrode_grid.cells.num);

    for i = 1 : number_of_states
        new_cell = states{i}.(ne).(am).(sd).cSurface ./ 1000;

        for j = 1 : length(new_cell)
            negative_electrode_concentration{i, j} = new_cell(j);
        end
    end

    % Electrolyte Concentration
    electrolyte_concentration = cell(number_of_states, electrolyte_grid.cells.num);

    for i = 1 : number_of_states
        new_cell = states{i}.(elyte).c ./ 1000;

        for j = 1 : length(new_cell)
            electrolyte_concentration{i, j} = new_cell(j);
        end
    end

    % Positive Electrode Concentration
    positive_electrode_concentration = cell(number_of_states, positive_electrode_grid.cells.num);

    for i = 1 : number_of_states
        new_cell = states{i}.(pe).(am).(sd).cSurface ./ 1000;

        for j = 1 : length(new_cell)
            positive_electrode_concentration{i, j} = new_cell(j);
        end
    end

    % Negative Electrode Potential
    negative_electrode_potential = cell(number_of_states, negative_electrode_grid.cells.num);

    for i = 1 : number_of_states
        new_cell = states{i}.(ne).(am).phi;

        for j = 1 : length(new_cell)
            negative_electrode_potential{i, j} = new_cell(j);
        end
    end

    % Electrolyte Potential
    electrolyte_potential = cell(number_of_states, electrolyte_grid.cells.num);

    for i = 1 : number_of_states
        new_cell = states{i}.(elyte).phi;

        for j = 1 : length(new_cell)
            electrolyte_potential{i, j} = new_cell(j);
        end
    end

    % Positive Electrode Potential
    positive_electrode_potential = cell(number_of_states, positive_electrode_grid.cells.num);

    for i = 1 : number_of_states
        new_cell = states{i}.(ne).(am).phi;

        for j = 1 : length(new_cell)
            positive_electrode_potential{i, j} = new_cell(j);
        end
    end

%    plotDashboard(output.model, output.states, 'step', 0);

    result = {number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential};

end
