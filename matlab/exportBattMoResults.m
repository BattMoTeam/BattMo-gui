%function output = exportBattMoResults(model,states)
    % Export BattMo output

    %% Create HDF5 structure
    nts = numel(states);
    nc = model.G.cells.num;
    nc_elyte = model.Electrolyte.G.cells.num;
    nc_ne = model.NegativeElectrode.G.cells.num;
    nc_pe = model.PositiveElectrode.G.cells.num;
    
    N_ne = model.NegativeElectrode.ActiveMaterial.SolidDiffusion.N;
    N_pe = model.PositiveElectrode.ActiveMaterial.SolidDiffusion.N;
    
    fname = fullfile(ROOTDIR,'..','..','output','runBattery1D_results.h5');

    % Grid group
    gdim = model.G.griddim;

    switch gdim
        case 1
            h5create(fname,'/Grid/x',[nc 1]);
        case 2
            h5create(fname,'/Grid/x',[nc 1]);
            h5create(fname,'/Grid/y',[nc 1]);
        case 3
            error('Export not implemented for 3D grids')
    end
    
    
    % GlobalVariables group
    h5create(fname,'/GlobalVariables/time',[nts 1]);
    h5create(fname,'/GlobalVariables/I',[nts 1]);    
    h5create(fname,'/GlobalVariables/E',[nts 1]); 
    
    % ThermalModel group 
    for i = 1:nts
        datapath = ['/ThermalModel/',num2str(i),'/T'];
        h5create(fname,datapath,[nc 1]);
    end
    
    % Electrolyte group 
    h5create(fname,'/Electrolyte/IndexMap_elyte',[nc_elyte 1]); 
    for i = 1:nts
        datapath = ['/Electrolyte/',num2str(i),'/c'];
        h5create(fname,datapath,[nc_elyte 1]);
        datapath = ['/Electrolyte/',num2str(i),'/phi'];
        h5create(fname,datapath,[nc_elyte 1]);
    end    
    
    % NegativeElectrode group 
    h5create(fname,'/NegativeElectrode/IndexMap_ne',[nc_ne 1]); 
    for i = 1:nts
        datapath = ['/NegativeElectrode/',num2str(i),'/cSurface'];
        h5create(fname,datapath,[nc_ne 1]);
        datapath = ['/NegativeElectrode/',num2str(i),'/phi'];
        h5create(fname,datapath,[nc_ne 1]);
        datapath = ['/NegativeElectrode/',num2str(i),'/SolidDiffusion/c'];
        h5create(fname,datapath,[nc_ne*N_ne 1]);
    end    
    
    % PositiveElectrode group 
    h5create(fname,'/PositiveElectrode/IndexMap_ne',[nc_pe 1]); 
    for i = 1:nts
        datapath = ['/PositiveElectrode/',num2str(i),'/cSurface'];
        h5create(fname,datapath,[nc_pe 1]);
        datapath = ['/PositiveElectrode/',num2str(i),'/phi'];
        h5create(fname,datapath,[nc_pe 1]);
        datapath = ['/PositiveElectrode/',num2str(i),'/SolidDiffusion/c'];
        h5create(fname,datapath,[nc_pe*N_pe 1]);
    end        
    
    %% Write HDF5 datasets from state

    % Grid group
    h5write(fname,'/Grid/x',model.G.cells.centroids(:,1));
    if numel(model.G.cartDims) == 2
        h5write(fname,'/Grid/y',model.G.cells.centroids(:,2));
    end
    
    % GlobalVariables group
    outputvars = model.extractGlobalVariables(states);
    
    h5write(fname,'/GlobalVariables/time',cellfun(@(x) x.time, outputvars)');
    h5write(fname,'/GlobalVariables/I',cellfun(@(x) x.I, outputvars)');
    h5write(fname,'/GlobalVariables/E',cellfun(@(x) x.E, outputvars)'); 
    
    % ThermalModel group 
    
    for i = 1:nts
        datapath = ['/ThermalModel/',num2str(i),'/T'];
        h5write(fname,datapath,states{i}.ThermalModel.T);
    end
    
    % Electrolyte group 
    h5write(fname,'/Electrolyte/IndexMap_elyte',model.Electrolyte.G.cells.indexMap);
    for i = 1:nts
        datapath = ['/Electrolyte/',num2str(i),'/c'];
        h5write(fname,datapath,states{i}.Electrolyte.c);
        datapath = ['/Electrolyte/',num2str(i),'/phi'];
        h5write(fname,datapath,states{i}.Electrolyte.phi);
    end    
    
    % NegativeElectrode group 
    h5write(fname,'/NegativeElectrode/IndexMap_ne',model.NegativeElectrode.G.cells.indexMap);
    for i = 1:nts
        % Have put this in this group as it is defined on the cells in the main grid.
        % Maybe change it later?
        datapath = ['/NegativeElectrode/',num2str(i),'/cSurface'];  
        h5write(fname,datapath,states{i}.NegativeElectrode.ActiveMaterial.SolidDiffusion.cSurface);
        datapath = ['/NegativeElectrode/',num2str(i),'/phi'];
        h5write(fname,datapath,states{i}.NegativeElectrode.ActiveMaterial.phi);
        datapath = ['/NegativeElectrode/',num2str(i),'/SolidDiffusion/c'];
        h5write(fname,datapath,states{i}.NegativeElectrode.ActiveMaterial.SolidDiffusion.c);
    end    
    
    % PositiveElectrode group 
    h5write(fname,'/PositiveElectrode/IndexMap_ne',model.PositiveElectrode.G.cells.indexMap);
    for i = 1:nts
        % Have put this in this group as it is defined on the cells in the main grid.
        % Maybe change it later?
        datapath = ['/PositiveElectrode/',num2str(i),'/cSurface'];  
        h5write(fname,datapath,states{i}.PositiveElectrode.ActiveMaterial.SolidDiffusion.cSurface);
        datapath = ['/PositiveElectrode/',num2str(i),'/phi'];
        h5write(fname,datapath,states{i}.PositiveElectrode.ActiveMaterial.phi);
        datapath = ['/PositiveElectrode/',num2str(i),'/SolidDiffusion/c'];
        h5write(fname,datapath,states{i}.PositiveElectrode.ActiveMaterial.SolidDiffusion.c);
    end    
    
%% 

h5disp(fname)
    