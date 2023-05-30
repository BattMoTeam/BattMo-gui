function obj = EnergyOutput(model, states, schedule, varargin)

    opt     = struct('Price'          , 1.0  , ...
                     'ComputePartials', false, ...
                     'tStep'          , []   , ...
                     'state'          , []   , ...
                     'from_states'    , true);
    opt     = merge_options(opt, varargin{:});
    
    dts   = schedule.step.val;

    tSteps = opt.tStep;
    
    if isempty(tSteps) %do all
        time = 0;
        numSteps = numel(dts);
        tSteps = (1:numSteps)';
    else
        time = sum(dts(1:(opt.tStep-1)));
        numSteps = 1;
        dts = dts(opt.tStep);
    end

    obj = repmat({[]}, numSteps, 1);

    for step = 1:numSteps
        dt = dts(step);
        state = states{tSteps(step)};
        if opt.ComputePartials
            if (opt.from_states) 
                state = model.initStateAD(state);
            else
                state = opt.state;
            end
            E = state.Control.E;
            I = state.Control.I;
        else
            E = state.Control.E;
            I = state.Control.I; 
        end
        obj{step} = opt.Price*I*E*dt;
    end
    
end


%{
Copyright 2021-2023 SINTEF Industry, Sustainable Energy Technology
and SINTEF Digital, Mathematics & Cybernetics.

This file is part of The Battery Modeling Toolbox BattMo

BattMo is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

BattMo is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with BattMo.  If not, see <http://www.gnu.org/licenses/>.
%}