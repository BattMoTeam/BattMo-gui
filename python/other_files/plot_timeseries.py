from h5py import File, Group, Dataset
import numpy as np
from bokeh.io import show, save
from bokeh.layouts import row, column, Spacer
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Select, CustomJS



class AppTimeSeries:
    """
    -- Insert here final description --.

    Parameters:
        data_dict: dict
            dictionary of (col_name_string, array) pairs.
    """
    
    def __init__(self,
                 time: np.array,
                 voltage: np.array,
                 current: np.array
                 ) -> None:

        self.data = {"Time" : time,
                    "Voltage": voltage,
                    "Current":current}



        self.validate_data()
        self.calculate_capacity()
        self.build_data_sources()
        self.create_widgets()
        self.create_plot()
        self.style_plot()
        self.attach_js_code()
        self.app = self.assemble_layout()


    def validate_data(self):


        lens_of_arrays = []

        for key, array in self.data.items():

            assert isinstance(array, np.ndarray), f"what is stored in {key} is not a numpy array"
            assert len(array.shape) <= 2, f"the array in {key} has {len(array.shape)} dimensions"
            assert min(array.shape) == 1, f"the array in {key} is not 1D: shape {array.shape}"
          
            self.data[key] = array.flatten() #transform to 1D array

            lens_of_arrays.append(self.data[key].shape)

        assert all(x==lens_of_arrays[0] for x in lens_of_arrays), f"Not all arrays have same dimension."

        self.npoints = lens_of_arrays[0]




    def calculate_capacity(self):
        
        self.data["Capacity"] = np.cumsum( np.multiply(self.data["Time"], self.data["Current"]) )



    def build_data_sources(self):


        self.full_data_source = ColumnDataSource(data=self.data)

        self.default_x = "Time"
        self.default_y = "Voltage"

        self.render_data_source = ColumnDataSource(data={"x":self.data[self.default_x],
                                                        "y":self.data[self.default_y]})      

        

    
    def create_widgets(self):

        self.x_selector = Select(title="x", 
                                options=list(self.data.keys()), 
                                value=self.default_x, width=200)

        self.y_selector = Select(title="y", 
                                options=list(self.data.keys()), 
                                value=self.default_y, width=200)


    def create_plot(self):
        self.plot = figure(frame_height=400,
                    frame_width=1000,
                    x_axis_label=self.default_x,
                    y_axis_label=self.default_y)

        self.glyph = self.plot.circle(source=self.render_data_source, 
                                    x="x", y="y")        


    def style_plot(self):

        self.plot.toolbar.logo = None
        self.plot.xaxis.axis_label_text_font_size = "20pt"
        self.plot.yaxis.axis_label_text_font_size = "20pt"
        self.plot.xaxis.major_label_text_font_size = "15pt"
        self.plot.yaxis.major_label_text_font_size = "15pt"

        self.glyph.glyph.size = 15         
        self.glyph.glyph.fill_color="#04bfbf"
        self.glyph.glyph.line_color="#04bfbf"
        
        self.x_selector



    def attach_js_code(self):
        
        js_code = """

        render_source.data['x'] = [];
        render_source.data['y'] = [];

        for (var i = 0; i < npoints; i++) {

            render_source.data['x'].push(full_source.data[x_selector.value][i]);
            render_source.data['y'].push(full_source.data[y_selector.value][i]);            
        }

        xaxis[0].axis_label = x_selector.value;
        yaxis[0].axis_label = y_selector.value;

        render_source.change.emit();

        """

        args = dict(
            npoints = self.npoints,
            full_source = self.full_data_source, 
            render_source = self.render_data_source,
            x_selector = self.x_selector, 
            y_selector = self.y_selector,
            xaxis=self.plot.xaxis,
            yaxis=self.plot.yaxis
        )

        self.x_selector.js_on_change("value", CustomJS(code=js_code, args=args))
        self.y_selector.js_on_change("value", CustomJS(code=js_code, args=args))



    def assemble_layout(self):

        layout = column(self.x_selector,
                        Spacer(height=15),
                        self.y_selector,
                        Spacer(width=15),
                        self.plot
                        )

        return layout


    #Public methods
            
        
    def render_app(self):
        show(self.app)


    def save_app(self, path_to_save:str):
        save(self.app, path_to_save)

