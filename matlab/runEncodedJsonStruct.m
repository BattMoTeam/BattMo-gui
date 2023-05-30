function result = runEncodedJsonStruct()
    jsonfilename = fullfile('battmo_formatted_input.json');
    jsonstruct = parseBattmoJson(jsonfilename);
    jsonstruct.Geometry.case = jsonstruct.Geometry.xCase;
    % jsonstruct.Geometry.case doesn't exist (why??), instead there's xCase

    % Run battery simulation with function that takes json input
    output = runBatteryJson(jsonstruct);

    states = output.states;

    result_E = cellfun(@(x) x.Control.E, states);
    result_I = cellfun(@(x) x.Control.I, states);
    time = cellfun(@(x) x.time, states);
    result_time = time/hour;


%    plotDashboard(output.model, output.states, 'step', 0);

    result = [result_E, result_I, result_time];

end
