function [points, cells] = getVTKPointsCells(G)

% Function to extract point and cell data from MRST grid in correct order
% for using t create VTK unstructured grid.
%
% NB: 
% Currently only works for grids with single cell types based on
% tensorGrid. 
% Only works for 1D and 3D grids. Wrong ordering in 2D!

    assert(G.griddim ~= 2, 'Error: Does not work for 2D grids.')

    nn = unique(diff(G.faces.nodePos)).*2;
    nf = unique(diff(G.cells.facePos));
    
    assert(numel(nf)==1, 'Error: All cells in grid must have same number of nodes.')
    
    % Get points
    points = G.nodes.coords;

    % Points need 3 coords. Set undefined coords to 0.    
    sz = size(points);
    points = [points zeros(sz(1),3-sz(2))];
    
    % Some magic written by Bård to get cells in correct order
    ft = repmat((1:nf).', [G.cells.num,1]);
    pick = false(nf,1); pick([nf-1,nf])=true; pick(ft);
    fn=reshape(G.faces.nodes,nn./2,[]).';
    nodes = fn(G.cells.faces(pick(ft)),:);
    cells = [nodes(1:2:end,:), nodes(2:2:end,:)];
    cells = [repmat(nn,size(cells,1),1) cells];

    

end
