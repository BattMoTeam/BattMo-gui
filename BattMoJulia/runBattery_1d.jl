using BattMo

function runBattery_1d(;
    input = None,
    extra_timing  = false,
    linear_solver = :direct,
    general_ad    = false,
    use_groups    = false,
    kwarg...)

    sim, forces, state0, parameters, model = setup_sim_1d(input, use_groups = use_groups, general_ad = general_ad)

    total = jsondict["TimeStepping"]["totalTime"]
    n     = jsondict["TimeStepping"]["N"]

    dt = total/n
    timesteps = rampupTimesteps(total, dt, 5);    
    
    cfg = simulator_config(sim; kwarg...)
    cfg[:linear_solver]              = battery_linsolve(model, linear_solver)
    cfg[:debug_level]                = 0
    cfg[:max_residual]               = 1e20
    cfg[:min_nonlinear_iterations]   = 1
    cfg[:extra_timing]               = extra_timing
    cfg[:safe_mode]                  = false
    cfg[:error_on_incomplete]        = false
    cfg[:failure_cuts_timestep]      = true
    
    if false
        cfg[:info_level]               = 5
        cfg[:max_nonlinear_iterations] = 1
        cfg[:max_timestep_cuts]        = 0
    end

    cfg[:tolerances][:PP][:default] = 1e-1
    cfg[:tolerances][:BPP][:default] = 1e-1
    # Run simulation
    
    states, reports = simulate(sim, timesteps, forces = forces, config = cfg)

    extra = Dict(:model      => model,
                 :state0     => state0,
                 :parameters => parameters,
                 :timesteps  => timesteps,
                 :config     => cfg,
                 :forces     => forces,
                 :simulator  => sim)

    return (states = states, reports = reports, extra = extra)
end