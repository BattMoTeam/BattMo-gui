module runP2DBattery

    using BattMo, Logging,Jutul
    using HTTP
    using HTTP.WebSockets

    export runP2DBatt

    

    function runP2DBatt(json_file,ws)
        log_messages = String[]
        log_buffer = nothing
        # number_of_states = 0 
        # cell_voltage = 0
        # cell_current = 0
        # time_values = 0
        # negative_electrode_grid = 0
        # electrolyte_grid = 0
        # positive_electrode_grid = 0
        # negative_electrode_grid_bc = 0
        # electrolyte_grid_bc = 0
        # positive_electrode_grid_bc = 0
        # negative_electrode_concentration = 0
        # electrolyte_concentration = 0
        # positive_electrode_concentration = 0
        # negative_electrode_potential = 0
        # electrolyte_potential = 0
        # positive_electrode_potential = 0
        json_file = JSONFile(json_file)

        log_file = "simulation_log.log"  # Define the log file name
        open(log_file, "w") do file

            redirect_stdout(file)
            redirect_stderr(file)

            try
                # Create a custom IOBuffer to capture log messages
                log_buffer = IOBuffer();

                # Redirect the logger to use the custom IOBuffer
                global_logger(ConsoleLogger(log_buffer));

                # buf = IOBuffer()
                # redirect_stdout(buf) do
                fraction_tot = 0
                dt_tot = 0
                i = 0
                print("Calling BattMo simulation")
                # WebSockets.send(ws, "Pre-processing done")
                states,_ , _, extra = run_battery_test(json_file,fraction_tot=fraction_tot,dt_tot=dt_tot,i=i,ws = ws);
                # states,cellSpecifications , reports, extra = run_battery(json_file, max_timestep_cuts = 10);

                energy_efficiency = computeEnergyEfficiency(states);
                discharge_energy = computeCellEnergy(states);

                # end
                
                # energy_efficiency, init2,_ = computeEnergyEfficiency(json_file)
                # discharge_energy,_,_ = computeDischargeEnergy(json_file)

                print("Simulation finished")
                
                # file = "./"*output_path*"/jutul_1.jld2"
                # output_1 = JLD2.load(file)


                # print(output_1)

                con = BattMo.Constants();

                # Get some result values
                println("Number of states = ", size(states))
                number_of_states = size(states);
                timesteps = extra[:timesteps];
                time_values = cumsum(timesteps)/con.hour;
                cell_voltage = [state[:Control][:Phi][1] for state in states];
                cell_current = [state[:Control][:Current][1] for state in states];
                negative_electrode_grid_wrap = physical_representation(extra[:model][:NeAm]);
                electrolyte_grid_wrap = physical_representation(extra[:model][:Elyte]);
                positive_electrode_grid_wrap = physical_representation(extra[:model][:PeAm]);
                negative_electrode_concentration = Array([[state[:NeAm][:Cs] for state in states]/1000]);
                electrolyte_concentration = [state[:Elyte][:C] for state in states]/1000;
                positive_electrode_concentration = Array([[state[:PeAm][:Cs] for state in states]]/1000);
                negative_electrode_potential = [state[:NeAm][:Phi] for state in states];
                electrolyte_potential = [state[:Elyte][:Phi] for state in states];
                positive_electrode_potential = [state[:PeAm][:Phi] for state in states];

                nsteps = length(cell_voltage);
                time_values = time_values[1 : nsteps];

                # Mesh cell centroids coordinates
                centroids_NeAm = negative_electrode_grid_wrap[:cell_centroids, Cells()];
                centroids_Elyte = electrolyte_grid_wrap[:cell_centroids, Cells()];
                centroids_PeAm = positive_electrode_grid_wrap[:cell_centroids, Cells()];

                # Boundary faces coordinates
                boundaries_NeAm = negative_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()];
                boundaries_Elyte = electrolyte_grid_wrap[:boundary_centroids, BoundaryFaces()];
                boundaries_PeAm = positive_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()];

                # Create grid arrays

                # negative_electrode_grid = [centroids_NeAm, boundaries_NeAm].*10^6
                # electrolyte_grid = [centroids_Elyte, boundaries_Elyte].*10^6
                # positive_electrode_grid = [centroids_PeAm, boundaries_PeAm].*10^6

                negative_electrode_grid = centroids_NeAm.*10^6;
                negative_electrode_grid_bc = boundaries_NeAm.*10^6;
                electrolyte_grid = centroids_Elyte.*10^6;
                electrolyte_grid_bc = boundaries_Elyte.*10^6;
                positive_electrode_grid = centroids_PeAm.*10^6;
                positive_electrode_grid_bc = boundaries_PeAm.*10^6;
                negative_electrode_concentration = negative_electrode_concentration[1];
                positive_electrode_concentration = positive_electrode_concentration[1];

                # Capture log messages
                # seekstart(log_buffer);
                log_messages = split(String(take!(log_buffer)), "\n");
                println("Number of states 2 = ", number_of_states)
                
                return log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential,discharge_energy,energy_efficiency
            catch e
                println("Simulation failed: $e")

                number_of_states = [0]
                cell_voltage = [0]
                cell_current = [0]
                time_values = [0]
                negative_electrode_grid = [0]
                negative_electrode_grid_bc = [0]
                electrolyte_grid = [0]
                electrolyte_grid_bc = [0]
                positive_electrode_grid = [0]
                positive_electrode_grid_bc = [0]
                negative_electrode_concentration = [0]
                electrolyte_concentration = [0]
                positive_electrode_concentration = [0]
                negative_electrode_potential = [0]
                electrolyte_potential = [0]
                positive_electrode_potential = [0]
                discharge_energy = [0]
                energy_efficiency = [0]

                # Capture log messages
                seekstart(log_buffer);
                log_messages = split(String(take!(log_buffer)), "\n");
                return log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential,discharge_energy,energy_efficiency

            finally
                close(log_buffer)  
            end
        end

        #return log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential
    end

    function send_simulation_progress(ws::WebSocket, progress::Float64)
        try
            WebSockets.send(ws, "Simulation progress: $progress")
        catch e
            @error "Failed to send progress update: $e"
        end
    end


    function setup_config_test(sim::Jutul.JutulSimulator,
            model::MultiModel,
            linear_solver::Symbol,
            extra_timing::Bool,
            timesteps,
            fraction_tot,
            dt_tot,
            i,
            ws::WebSocket;
            kwarg...)
        """
        Sets up the config object used during simulation. In this current version this
        setup is the same for json and mat files. The specific setup values should
        probably be given as inputs in future versions of BattMo.jl
        """

        cfg = simulator_config(sim; kwarg...);

        cfg[:linear_solver]              = BattMo.battery_linsolve(model, linear_solver);
        cfg[:debug_level]                = 0
        #cfg[:max_timestep_cuts]         = 0
        cfg[:max_residual]               = 1e20
        cfg[:min_nonlinear_iterations]   = 1
        cfg[:extra_timing]               = extra_timing
        # cfg[:max_nonlinear_iterations] = 5
        cfg[:safe_mode]                  = false
        cfg[:error_on_incomplete]        = false
        #Original matlab steps will be too large!
        cfg[:failure_cuts_timestep]      = true

        for key in Jutul.submodels_symbols(model)
            cfg[:tolerances][key][:default]  = 1e-5
        end

        if model[:Control].system.policy isa CyclingCVPolicy

            cfg[:tolerances][:global_convergence_check_function] = (model, storage) -> BattMo.check_constraints(model, storage);

            function post_hook(done, report, sim, dt, forces, max_iter, cfg)

                s = Jutul.get_simulator_storage(sim);
                m = Jutul.get_simulator_model(sim);

                if s.state.Control.ControllerCV.numberOfCycles >= m[:Control].system.policy.numberOfCycles
                    report[:stopnow] = true
                else
                    report[:stopnow] = false
                end

                if done 
                    i +=1
                    total_time = sum(timesteps)
                    println("total time = ", total_time)
                    dt_tot += dt
                    println("progress dt= ", dt_tot)
                    fraction = dt/total_time
                    fraction_tot += fraction
                    println("progress fraction= ", fraction_tot)
                    println("progress i= ", i)
                    send_simulation_progress(ws,fraction)
                end

                return (done, report)

            end

            cfg[:post_ministep_hook] = post_hook

        end

        return cfg

    end

    function run_battery_test(init::InputFile;   
                            use_p2d::Bool                     = true,
                            extra_timing::Bool                = false,
                            max_step::Union{Integer, Nothing} = nothing,
                            linear_solver::Symbol             = :direct,
                            general_ad::Bool                  = false,
                            use_groups::Bool                  = false,
                            fraction_tot,
                            dt_tot,
                            i,
                            ws::WebSocket                     = nothing,
                            kwarg...)
        """
        Run battery wrapper method. Can use inputs from either Matlab or Json files and performs
        simulation using a simple discharge CV policy
        """

        #Setup simulation
        sim, forces, state0, parameters, init, model = BattMo.setup_sim(init, use_p2d=use_p2d, use_groups=use_groups, general_ad=general_ad);

        #Set up config and timesteps
        timesteps = BattMo.setup_timesteps(init; max_step = max_step);
        cfg = setup_config_test(sim, model, linear_solver, extra_timing,timesteps,fraction_tot,dt_tot,i,ws; kwarg...);
        # cfg = BattMo.setup_config(sim, model, linear_solver, extra_timing; kwarg...);

        # Perform simulation
        states, reports = BattMo.simulate(state0, sim, timesteps, forces=forces, config=cfg);


        extra = Dict(:model => model,
                    :state0 => state0,
                    :parameters => parameters,
                    :init => init,
                    :timesteps => timesteps,
                    :config => cfg,
                    :forces => forces,
                    :simulator => sim);

        cellSpecifications = BattMo.computeCellSpecifications(model);
        println("Number of states 1 = ", size(states))

        return (states             = states            ,
                cellSpecifications = cellSpecifications, 
                reports            = reports           ,
                extra              = extra             ,
                exported           = init)

    end
end