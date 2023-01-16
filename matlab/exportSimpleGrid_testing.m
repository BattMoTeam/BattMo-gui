%% Testing grid export

model = getJellyRollModel();
% model = get3DexampleModel();
G = model.G;

% G = cartGrid([2,2,1]);
% G = cartGrid([2,3]);
% G = cartGrid([3]);


nn = unique(diff(G.faces.nodePos)).*2;
nf = unique(diff(G.cells.facePos));

assert(numel(nf)==1, 'Error: All cells in grid must have same number of nodes.')

points = G.nodes.coords;

sz = size(points);

points = [points zeros(sz(1),3-sz(2))];


ft = repmat((1:nf).', [G.cells.num,1]);
pick = false(nf,1); pick([nf-1,nf])=true; pick(ft);
fn=reshape(G.faces.nodes,nn./2,[]).';
nodes = fn(G.cells.faces(pick(ft)),:);
cells = [nodes(1:2:end,:), nodes(2:2:end,:)];
cells = [repmat(nn,size(cells,1),1) cells];


fname = fullfile('/home/francesca/battmo-github/BattMo-gui/data','jellyroll_Test.h5');
 
if ~exist(fname, 'file')

    h5create(fname,'/Grid/cells',size(cells));
    h5create(fname,'/Grid/points',size(points));

end
    
h5write(fname,'/Grid/cells',cells);
h5write(fname,'/Grid/points',points);


