import sys 
import os 
import numpy as np 
import json 
import csv 
from PySide6 .QtWidgets import (QApplication ,QMainWindow ,QVBoxLayout ,QHBoxLayout ,QWidget ,QPushButton ,QComboBox ,QListWidget ,QLabel ,QTableWidget ,QTableWidgetItem ,QFileDialog ,QScrollArea ,QSplitter ,QTabWidget ,QLineEdit ,QCheckBox ,QMessageBox ,QListWidgetItem ,QSpinBox ,QDialog ,QTextEdit ,QStyleFactory ,QGroupBox ,QGridLayout ,QFormLayout ,QDoubleSpinBox ,QLayout ,QLayoutItem )
from PySide6 .QtGui import QPalette ,QColor 
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QColor 
import matplotlib .pyplot as plt 
from matplotlib .backends .backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
import copy 
from matplotlib .backends .backend_qt5agg import NavigationToolbar2QT as NavigationToolbar 


class SDDatabaseViewer (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD Database Viewer")
        self .setGeometry (100 ,100 ,1200 ,800 )

        self .central_widget =QWidget ()
        self .setCentralWidget (self .central_widget )
        self .layout =QHBoxLayout (self .central_widget )

        self .loaded_data =None 
        self .original_data =None 
        self .current_folder =None 
        self .comparison_data ={}
        self .is_updating_plot_options =False 
        self .ml_variables =[]
        self .plot_options ={}

        self .plot_fitted_data_checkbox =QCheckBox ("Plot Fitted Data")
        self .plot_baseline_checkbox =QCheckBox ("Plot Baseline")

        self .file_type =None 
        self .plot_options_form =None 
        self .setup_ui ()
        self .setup_plotting_tab ()

    def setup_ui (self ):

        left_panel =QWidget ()
        left_layout =QVBoxLayout (left_panel )

        self .app_name_label =QLabel ("SD Database Viewer")
        self .app_name_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .app_name_label .setStyleSheet ("font-size: 22px; font-weight: bold;")
        self .email_label =QLabel ("shankar.dutt@anu.edu.au")
        self .email_label .setAlignment (Qt .AlignmentFlag .AlignCenter )

        left_layout .addWidget (self .app_name_label )
        left_layout .addWidget (self .email_label )

        self .file_type_combo =QComboBox ()
        self .file_type_combo .addItems ([".event_fitting.npz",".dataset.npz",".MLdataset.npz",".event_data.npz"])
        self .file_type_combo .currentIndexChanged .connect (self .update_file_list )
        left_layout .addWidget (QLabel ("Select File Type:"))
        left_layout .addWidget (self .file_type_combo )

        self .folder_button =QPushButton ("Select Folder")
        self .folder_button .clicked .connect (self .select_folder )
        left_layout .addWidget (self .folder_button )

        self .file_list =QListWidget ()
        self .file_list .setSelectionMode (QListWidget .SelectionMode .ExtendedSelection )
        left_layout .addWidget (QLabel ("Available Files:"))
        left_layout .addWidget (self .file_list )

        self .load_button =QPushButton ("Load Selected File(s)")
        self .load_button .clicked .connect (self .load_files )
        left_layout .addWidget (self .load_button )


        self .right_panel =QTabWidget ()


        data_preview_tab =QWidget ()
        data_preview_layout =QVBoxLayout (data_preview_tab )
        self .data_table =QTableWidget ()
        data_preview_layout .addWidget (self .data_table )
        self .right_panel .addTab (data_preview_tab ,"Data Preview")


        settings_tab =QWidget ()
        settings_layout =QVBoxLayout (settings_tab )
        self .settings_table =QTableWidget ()
        settings_layout .addWidget (self .settings_table )
        self .right_panel .addTab (settings_tab ,"Settings")


        filtering_tab =QWidget ()
        filtering_layout =QVBoxLayout (filtering_tab )


        filter_group =QGroupBox ("Filter Options")
        filter_group_layout =QVBoxLayout (filter_group )

        self .filter_layout =QVBoxLayout ()
        filter_scroll_area =QScrollArea ()
        filter_scroll_area .setWidgetResizable (True )
        filter_scroll_area_content =QWidget ()
        filter_scroll_area_content .setLayout (self .filter_layout )
        filter_scroll_area .setWidget (filter_scroll_area_content )
        filter_group_layout .addWidget (filter_scroll_area )

        add_filter_button =QPushButton ("Add Filter")
        add_filter_button .clicked .connect (self .add_filter )
        filter_group_layout .addWidget (add_filter_button )

        filtering_layout .addWidget (filter_group )


        action_group =QGroupBox ("Actions")
        action_layout =QHBoxLayout (action_group )

        apply_filters_button =QPushButton ("Apply Filters")
        apply_filters_button .clicked .connect (self .apply_filters )
        action_layout .addWidget (apply_filters_button )

        save_filtered_data_button =QPushButton ("Save Filtered Data")
        save_filtered_data_button .clicked .connect (self .save_filtered_data )
        action_layout .addWidget (save_filtered_data_button )

        filtering_layout .addWidget (action_group )

        self .right_panel .addTab (filtering_tab ,"Filtering")


        comparison_tab =QWidget ()
        comparison_layout =QVBoxLayout (comparison_tab )

        self .comparison_list =QListWidget ()
        comparison_layout .addWidget (QLabel ("Loaded Files for Comparison:"))
        comparison_layout .addWidget (self .comparison_list )

        comparison_buttons_layout =QHBoxLayout ()
        self .add_comparison_file_button =QPushButton ("Add File")
        self .add_comparison_file_button .clicked .connect (self .add_comparison_file )
        comparison_buttons_layout .addWidget (self .add_comparison_file_button )

        self .remove_comparison_file_button =QPushButton ("Remove File")
        self .remove_comparison_file_button .clicked .connect (self .remove_comparison_file )
        comparison_buttons_layout .addWidget (self .remove_comparison_file_button )

        comparison_layout .addLayout (comparison_buttons_layout )

        self .compare_button =QPushButton ("Compare Files")
        self .compare_button .clicked .connect (self .compare_files )
        comparison_layout .addWidget (self .compare_button )

        self .right_panel .addTab (comparison_tab ,"Comparison")


        splitter =QSplitter (Qt .Horizontal )
        splitter .addWidget (left_panel )
        splitter .addWidget (self .right_panel )


        splitter .setSizes ([100 ,700 ])

        self .layout .addWidget (splitter )

    def setup_plotting_tab (self ):
        plotting_tab =QWidget ()
        plotting_layout =QVBoxLayout (plotting_tab )

        self .plot_options_form =QFormLayout ()

        self .plot_type_combo =QComboBox ()
        self .plot_type_combo .currentIndexChanged .connect (self .on_plot_type_changed )

        self .x_variable_combo =QComboBox ()
        self .y_variable_combo =QComboBox ()
        self .event_number_combo =QComboBox ()

        self .event_range_start =QSpinBox ()
        self .event_range_end =QSpinBox ()
        range_layout =QHBoxLayout ()
        range_layout .addWidget (QLabel ("From:"))
        range_layout .addWidget (self .event_range_start )
        range_layout .addWidget (QLabel ("To:"))
        range_layout .addWidget (self .event_range_end )

        self .center_events_combo =QComboBox ()
        self .center_events_combo .addItems (["No Centering","Center on Minimum","Center on Maximum"])

        self .same_segments_checkbox =QCheckBox ("Plot events with same number of segments")
        self .same_segments_checkbox .stateChanged .connect (self .on_same_segments_changed )

        self .segments_number_combo =QComboBox ()

        self .plot_file_combo =QComboBox ()
        self .plot_file_combo .addItem ("Current File")

        self .plot_options ={
        "plot_type":(self .plot_type_combo ,"Select Plot Type:"),
        "x_variable":(self .x_variable_combo ,"Select X Variable:"),
        "y_variable":(self .y_variable_combo ,"Select Y Variable (for scatter):"),
        "event_number":(self .event_number_combo ,"Select Event:"),
        "event_range":(range_layout ,"Event Range:"),
        "center_events":(self .center_events_combo ,"Event Centering:"),
        "same_segments":(self .same_segments_checkbox ,""),
        "segments_number":(self .segments_number_combo ,"Select number of segments:"),
        "plot_file":(self .plot_file_combo ,"Select File to Plot:")
        }

        for option ,(widget ,label )in self .plot_options .items ():
            if isinstance (widget ,QLayout ):
                self .plot_options_form .addRow (label ,widget )
            else :
                self .plot_options_form .addRow (label ,widget )


        options_group =QGroupBox ("Plot Options")
        options_group .setLayout (self .plot_options_form )
        plotting_layout .addWidget (options_group )



        button_layout =QHBoxLayout ()
        self .plot_button =QPushButton ("Generate Plot")
        self .plot_button .clicked .connect (self .plot_data )
        button_layout .addWidget (self .plot_button )
        self .plot_fitted_data_checkbox =QCheckBox ("Plot Fitted Data")
        self .plot_baseline_checkbox =QCheckBox ("Plot Baseline")
        button_layout .addWidget (self .plot_fitted_data_checkbox )
        button_layout .addWidget (self .plot_baseline_checkbox )
        plotting_layout .addLayout (button_layout )


        self .figure =plt .figure (figsize =(5 ,4 ))
        self .canvas =FigureCanvas (self .figure )
        plotting_layout .addWidget (self .canvas )

        self .right_panel .addTab (plotting_tab ,"Plotting")

        self .hide_all_plot_widgets ()
        self .update_plot_options ()



    def hide_all_plot_widgets (self ):
        if self .plot_options_form is None :
            return 

        for i in range (self .plot_options_form .rowCount ()):
            label_item =self .plot_options_form .itemAt (i ,QFormLayout .LabelRole )
            field_item =self .plot_options_form .itemAt (i ,QFormLayout .FieldRole )

            if label_item and label_item .widget ():
                label_item .widget ().setVisible (False )

            if field_item :
                if isinstance (field_item ,QLayoutItem )and field_item .widget ():
                    field_item .widget ().setVisible (False )
                elif isinstance (field_item ,QLayout ):
                    for j in range (field_item .count ()):
                        if field_item .itemAt (j )and field_item .itemAt (j ).widget ():
                            field_item .itemAt (j ).widget ().setVisible (False )

        if hasattr (self ,'plot_fitted_data_checkbox'):
            self .plot_fitted_data_checkbox .setVisible (False )
        if hasattr (self ,'plot_baseline_checkbox'):
            self .plot_baseline_checkbox .setVisible (False )




    def add_comparison_file (self ):
        file_paths ,_ =QFileDialog .getOpenFileNames (self ,"Open NPZ File(s)","","NPZ Files (*.npz)")
        for file_path in file_paths :
            try :
                data =np .load (file_path ,allow_pickle =True )
                file_name =os .path .basename (file_path )
                self .comparison_data [file_name ]=data 
                self .comparison_list .addItem (file_name )
                self .plot_file_combo .addItem (file_name )
            except Exception as e :
                QMessageBox .critical (self ,"Error",f"Failed to load file {file_name }: {str (e )}")

        if file_paths :
            QMessageBox .information (self ,"Files Added",f"Added {len (file_paths )} file(s) to comparison")

    def remove_comparison_file (self ):
        selected_items =self .comparison_list .selectedItems ()
        if selected_items :
            for item in selected_items :
                file_name =item .text ()
                del self .comparison_data [file_name ]
                self .comparison_list .takeItem (self .comparison_list .row (item ))
                index =self .plot_file_combo .findText (file_name )
                if index !=-1 :
                    self .plot_file_combo .removeItem (index )
            QMessageBox .information (self ,"Files Removed",f"Removed {len (selected_items )} file(s) from comparison")

    def compare_files (self ):
        if len (self .comparison_data )<2 :
            QMessageBox .warning (self ,"Warning","Please add at least two files for comparison.")
            return 

        self .figure .clear ()
        ax =self .figure .add_subplot (111 )

        for file_name ,data in self .comparison_data .items ():
            if 'events'in data :
                events =data ['events']
                durations =[event ['end_time']-event ['start_time']for event in events ]
                amplitudes =[np .min (event ['event_data'])for event in events ]
                ax .scatter (durations ,amplitudes ,label =file_name ,alpha =0.5 )

        ax .set_xlabel ("Duration (s)")
        ax .set_ylabel ("Amplitude")
        ax .set_title ("Event Duration vs Amplitude Comparison")

        self .canvas .draw ()

    def select_folder (self ):
        folder =QFileDialog .getExistingDirectory (self ,"Select Folder")
        if folder :
            self .current_folder =folder 
            self .update_file_list ()










    def update_file_list (self ):
        if self .current_folder :
            file_type =self .file_type_combo .currentText ()
            self .file_list .clear ()


            matching_files =[]


            for file in os .listdir (self .current_folder ):
                if file .endswith (file_type ):
                    matching_files .append (file )


            matching_files .sort (key =str .lower )


            for file in matching_files :
                self .file_list .addItem (file )

    def load_files (self ):
        selected_items =self .file_list .selectedItems ()
        if not selected_items :
            QMessageBox .warning (self ,"No File Selected","Please select one or more files to load.")
            return 

        self .comparison_data .clear ()
        self .plot_file_combo .clear ()
        self .plot_file_combo .addItem ("Current File")

        for item in selected_items :
            file_name =item .text ()
            file_path =os .path .join (self .current_folder ,file_name )
            npz_file =np .load (file_path ,allow_pickle =True )

            data ={key :npz_file [key ]for key in npz_file .files }

            if len (selected_items )==1 :
                self .loaded_data =data 
                self .original_data =copy .deepcopy (data )
                self .file_type =self .determine_file_type (file_name )
            else :
                self .comparison_data [file_name ]=data 
                self .plot_file_combo .addItem (file_name )

        if len (selected_items )==1 :
            if self .file_type =='MLdataset':
                self .update_ml_variables ()
            self .update_plot_options ()
            if self .file_type =='event_fitting':
                self .populate_segments_number_combo ()
            self .display_data ()
            self .display_settings ()
            self .update_plotting_options ()
            self .update_filtering_options ()

            if self .file_type in ['event_fitting','event_data']:
                num_events =self .get_num_events ()
                self .event_number_combo .clear ()
                self .event_number_combo .addItems ([f"Event {i }"for i in range (num_events )])

            self .right_panel .setCurrentIndex (0 )
            self .populate_segments_number_combo ()
            self .on_plot_type_changed ()
        else :
            self .comparison_list .clear ()
            self .comparison_list .addItems (self .comparison_data .keys ())
            QMessageBox .information (self ,"Files Loaded",f"Loaded {len (selected_items )} files for comparison.")


    def update_filtering_options (self ):

        for i in reversed (range (self .filter_layout .count ())):
            self .filter_layout .itemAt (i ).widget ().deleteLater ()


        filtering_tab_index =self .right_panel .indexOf (self .right_panel .findChild (QWidget ,"Filtering"))
        self .right_panel .setTabEnabled (filtering_tab_index ,self .file_type in ['event_fitting','dataset','MLdataset'])

    def update_plotting_options (self ):
        self .is_updating_plot_options =True 
        self .plot_type_combo .clear ()
        if self .file_type is None :
            self .plot_type_label .setText ("No file loaded. Please load a file to see plotting options.")
            self .hide_all_plot_widgets ()
        elif self .file_type in ['dataset','MLdataset']:
            self .plot_type_combo .addItems (["X Data Variable Distribution","X Data Variable Scatter"])
            self .update_dataset_options ()
        elif self .file_type in ['event_fitting','event_data']:
            self .plot_type_combo .addItems (["Individual Event","Multiple Events","Scatter Plot"])
            self .update_event_options ()

        self .is_updating_plot_options =False 

    def update_dataset_options (self ):
        if self .file_type =='MLdataset':
            variables =self .ml_variables 
        else :
            variables =['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']

        self .x_variable_combo .clear ()
        self .y_variable_combo .clear ()
        self .x_variable_combo .addItems (variables )
        self .y_variable_combo .addItems (variables )



    def update_event_options (self ):
        if self .loaded_data is not None :
            num_events =self .get_num_events ()
            self .event_number_combo .clear ()
            self .event_number_combo .addItems ([f"Event {i }"for i in range (num_events )])
            self .event_range_start .setRange (0 ,max (0 ,num_events -1 ))
            self .event_range_end .setRange (0 ,max (0 ,num_events -1 ))
            self .event_range_end .setValue (min (9 ,max (0 ,num_events -1 )))



    def on_plot_type_changed (self ):
        if self .is_updating_plot_options :
            return 

        self .hide_all_plot_widgets ()
        plot_type =self .plot_type_combo .currentText ()

        self .show_plot_option ("plot_type")
        self .show_plot_option ("plot_file")
        self .plot_button .setVisible (True )

        if self .file_type in ['dataset','MLdataset']:
            self .show_plot_option ("x_variable")
            if plot_type =="X Data Variable Scatter":
                self .show_plot_option ("y_variable")
        elif self .file_type in ['event_fitting','event_data']:
            if plot_type =="Individual Event":
                self .show_plot_option ("event_number")
                self .show_plot_option ("center_events")
                if self .file_type =='event_fitting':
                    self .plot_fitted_data_checkbox .setVisible (True )
                    self .plot_baseline_checkbox .setVisible (True )
            elif plot_type =="Multiple Events":
                self .show_plot_option ("event_range")
                self .show_plot_option ("center_events")
                if self .file_type =='event_fitting':
                    self .show_plot_option ("same_segments")
                    is_checked =self .same_segments_checkbox .isChecked ()
                    if is_checked :
                        self .show_plot_option ("segments_number")
            elif plot_type =="Scatter Plot":
                self .show_plot_option ("x_variable")
                self .show_plot_option ("y_variable")

        if self .file_type =='event_fitting'and plot_type =="Multiple Events":
            self .populate_segments_number_combo ()


    def determine_file_type (self ,file_name ):
        if file_name .endswith ('.dataset.npz'):
            return 'dataset'
        elif file_name .endswith ('.event_fitting.npz'):
            return 'event_fitting'
        elif file_name .endswith ('.MLdataset.npz'):
            return 'MLdataset'
        elif file_name .endswith ('.event_data.npz'):
            return 'event_data'
        else :
            return 'unknown'


    def get_ml_scheme (self ):

        if 'settings'in self .loaded_data :

            settings =self .loaded_data ['settings']




            if isinstance (settings ,np .ndarray ):
                if settings .dtype .kind in ['U','S']:
                    settings =settings .item ()
                elif settings .dtype ==object and len (settings )>0 :
                    settings =settings [0 ]
                else :

                    return 'Unknown'


            if isinstance (settings ,str ):
                try :
                    settings_dict =json .loads (settings )

                    ml_standard =settings_dict .get ('ML_standard','Unknown')

                    return ml_standard 
                except json .JSONDecodeError as e :

                    return 'Unknown'
            else :

                return 'Unknown'
        else :

            return 'Unknown'

    def update_ml_variables (self ):
        scheme =self .get_ml_scheme ()








        if scheme =='Scheme 1':
            self .ml_variables =[f'part_{i }'for i in range (10 )]+['part_width']
        elif scheme =='Scheme 2':
            self .ml_variables =[f'part_{i }'for i in range (10 )]+['part_width','height','fwhm','heightatfwhm','area','width']
        elif scheme in ['Scheme 3','Scheme 4']:
            n_parts =10 if scheme =='Scheme 3'else 50 
            self .ml_variables =[f'part_{i }'for i in range (n_parts )]+['part_width','height','fwhm','heightatfwhm','area','width','skew','kurt']
        elif scheme =='Scheme 5':
            if 'X'in self .loaded_data and isinstance (self .loaded_data ['X'],np .ndarray ):
                signal_points =self .loaded_data ['X'].shape [1 ]-7 
                self .ml_variables =[f'signal_{i }'for i in range (signal_points )]+['height','fwhm','heightatfwhm','area','width','skew','kurt']
            else :

                self .ml_variables =['Unknown scheme']
        else :

            self .ml_variables =['Unknown scheme']



    def display_data (self ):
        if self .loaded_data is not None :
            self .clear_data_preview ()


            data_preview_tab =self .right_panel .widget (0 )
            data_preview_layout =data_preview_tab .layout ()


            self .data_table =QTableWidget ()
            self .data_table .setColumnCount (3 )
            self .data_table .setHorizontalHeaderLabels (["Key","Type","Value/Summary"])
            data_preview_layout .addWidget (self .data_table )

            if self .file_type in ['dataset','MLdataset']:
                self .display_dataset (data_preview_layout )
            elif self .file_type =='event_fitting':
                self .display_event_fitting ()
            elif self .file_type =='event_data':
                self .display_event_data ()
            else :
                self .display_generic ()

            self .data_table .resizeColumnsToContents ()


            self .right_panel .setCurrentIndex (0 )


    def clear_data_preview (self ):

        data_preview_tab =self .right_panel .widget (0 )


        if data_preview_tab .layout ()is not None :
            QWidget ().setLayout (data_preview_tab .layout ())


        QVBoxLayout (data_preview_tab )

    def display_dataset (self ,data_preview_layout ):
        main_splitter =QSplitter (Qt .Vertical )
        main_splitter .addWidget (self .data_table )


        for key ,value in self .loaded_data .items ():
            row =self .data_table .rowCount ()
            self .data_table .insertRow (row )
            self .data_table .setItem (row ,0 ,QTableWidgetItem (str (key )))
            self .data_table .setItem (row ,1 ,QTableWidgetItem (str (type (value ))))

            if key =='X'and isinstance (value ,np .ndarray ):
                self .data_table .setItem (row ,2 ,QTableWidgetItem ("See X Data details below"))
            elif key =='settings':
                self .data_table .setItem (row ,2 ,QTableWidgetItem ("See Settings tab for details"))
            else :
                self .data_table .setItem (row ,2 ,QTableWidgetItem (str (value )))


        if self .file_type =='MLdataset':
            scheme =self .get_ml_scheme ()
            row =self .data_table .rowCount ()
            self .data_table .insertRow (row )
            self .data_table .setItem (row ,0 ,QTableWidgetItem ("ML Scheme"))
            self .data_table .setItem (row ,1 ,QTableWidgetItem ("String"))
            self .data_table .setItem (row ,2 ,QTableWidgetItem (scheme ))


        if 'X'in self .loaded_data and isinstance (self .loaded_data ['X'],np .ndarray ):
            x_data_widget =QWidget ()
            x_data_layout =QVBoxLayout (x_data_widget )

            x_data_splitter =QSplitter (Qt .Vertical )


            summary_table =QTableWidget ()
            summary_table .setColumnCount (5 )
            summary_table .setHorizontalHeaderLabels (["Variable","Mean","Std","Min","Max"])
            x_data_layout .addWidget (QLabel ("X Data Summary:"))

            X_data =self .loaded_data ['X']


            if self .file_type =='MLdataset':
                variables =self .ml_variables 
            else :
                variables =['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']

            for i ,var in enumerate (variables ):
                summary_table .insertRow (i )
                col_data =X_data [:,i ]
                summary_table .setItem (i ,0 ,QTableWidgetItem (var ))
                summary_table .setItem (i ,1 ,QTableWidgetItem (f"{col_data .mean ():.8f}"))
                summary_table .setItem (i ,2 ,QTableWidgetItem (f"{col_data .std ():.8f}"))
                summary_table .setItem (i ,3 ,QTableWidgetItem (f"{col_data .min ():.8f}"))
                summary_table .setItem (i ,4 ,QTableWidgetItem (f"{col_data .max ():.8f}"))

            summary_table .resizeColumnsToContents ()
            x_data_splitter .addWidget (summary_table )


            control_widget =QWidget ()
            control_layout =QHBoxLayout (control_widget )
            control_layout .addWidget (QLabel ("Number of rows to display:"))
            self .row_spinner =QSpinBox ()
            self .row_spinner .setRange (1 ,1000000 )
            self .row_spinner .setValue (100 )
            control_layout .addWidget (self .row_spinner )
            refresh_button =QPushButton ("Refresh")
            refresh_button .clicked .connect (self .refresh_raw_data )
            control_layout .addWidget (refresh_button )


            raw_data_widget =QWidget ()
            raw_data_layout =QVBoxLayout (raw_data_widget )
            raw_data_layout .addWidget (control_widget )
            raw_data_layout .addWidget (QLabel ("Raw X Data:"))
            self .raw_data_table =QTableWidget ()
            self .raw_data_table .setColumnCount (len (variables ))
            self .raw_data_table .setHorizontalHeaderLabels (variables )
            raw_data_layout .addWidget (self .raw_data_table )

            self .refresh_raw_data ()

            x_data_splitter .addWidget (raw_data_widget )
            x_data_layout .addWidget (x_data_splitter )

            main_splitter .addWidget (x_data_widget )


        data_preview_layout .addWidget (main_splitter )


        main_splitter .setSizes ([100 ,300 ])
        if 'X'in self .loaded_data :
            x_data_splitter .setSizes ([100 ,200 ])

    def on_same_segments_changed (self ,state ):
        is_checked =(state ==Qt .CheckState .Checked .value )
        self .plot_options ["segments_number"][0 ].setVisible (is_checked )
        if is_checked :
            self .populate_segments_number_combo ()

    def populate_segments_number_combo (self ):
        self .segments_number_combo .clear ()
        if self .loaded_data is None or self .file_type !='event_fitting':
            return 

        segment_numbers =set ()
        for key ,value in self .loaded_data .items ():
            if 'SEGMENT_INFO_'in key and 'number_of_segments'in key :
                if isinstance (value ,np .ndarray ):
                    segment_numbers .update (value .astype (int ))
                elif isinstance (value ,(int ,float )):
                    segment_numbers .add (int (value ))

        for num in sorted (segment_numbers ):
            self .segments_number_combo .addItem (str (num ))



    def display_event_fitting (self ):
        if self .loaded_data is None :
            return 


        self .data_table .setRowCount (0 )
        self .data_table .setColumnCount (4 )
        self .data_table .setHorizontalHeaderLabels (["Event","Type","Summary","Actions"])


        event_analysis_tab =QWidget ()
        event_analysis_layout =QVBoxLayout (event_analysis_tab )
        self .right_panel .addTab (event_analysis_tab ,"Event Analysis")


        self .event_analysis_table =QTableWidget ()
        self .event_analysis_table .setColumnCount (10 )
        self .event_analysis_table .setHorizontalHeaderLabels (['Event ID','height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time'])
        event_analysis_layout .addWidget (self .event_analysis_table )

        event_counter =0 
        while True :
            event_key =f'EVENT_DATA_{event_counter }'
            if f'{event_key }_part_0'not in self .loaded_data :
                break 

            row =self .data_table .rowCount ()
            self .data_table .insertRow (row )
            self .data_table .setItem (row ,0 ,QTableWidgetItem (f"Event {event_counter }"))
            self .data_table .setItem (row ,1 ,QTableWidgetItem ("Event Data"))


            time_points =self .loaded_data [f'{event_key }_part_0']
            event_data =self .loaded_data [f'{event_key }_part_1']
            summary =f"Duration: {(time_points [-1 ]-time_points [0 ])*1e6 :.1f}us, Points: {len (event_data )}"
            self .data_table .setItem (row ,2 ,QTableWidgetItem (summary ))


            action_widget =QWidget ()
            action_layout =QHBoxLayout (action_widget )
            view_button =QPushButton ("View")
            view_button .clicked .connect (lambda _ ,ec =event_counter :self .view_event_details (ec ))
            action_layout .addWidget (view_button )
            self .data_table .setCellWidget (row ,3 ,action_widget )


            event_analysis_key =f'EVENT_ANALYSIS_{event_counter }'
            if event_analysis_key in self .loaded_data :
                event_analysis =self .loaded_data [event_analysis_key ]
                self .event_analysis_table .insertRow (event_counter )
                self .event_analysis_table .setItem (event_counter ,0 ,QTableWidgetItem (str (event_counter )))
                for i ,value in enumerate (event_analysis ):
                    self .event_analysis_table .setItem (event_counter ,i +1 ,QTableWidgetItem (f"{value :.8f}"))

            event_counter +=1 

        self .data_table .resizeColumnsToContents ()
        self .event_analysis_table .resizeColumnsToContents ()



    def view_event_details (self ,event_counter ):
        dialog =QDialog (self )
        dialog .setWindowTitle (f"Event {event_counter } Details")
        dialog .setMinimumSize (800 ,600 )

        layout =QVBoxLayout (dialog )


        nav_layout =QHBoxLayout ()
        prev_button =QPushButton ("Previous Event")
        next_button =QPushButton ("Next Event")
        nav_layout .addWidget (prev_button )
        nav_layout .addWidget (next_button )
        layout .addLayout (nav_layout )


        tab_widget =QTabWidget ()
        layout .addWidget (tab_widget )


        event_plot_tab =QWidget ()
        event_plot_layout =QVBoxLayout (event_plot_tab )
        event_figure =plt .figure (figsize =(5 ,4 ))
        event_canvas =FigureCanvas (event_figure )
        event_plot_layout .addWidget (event_canvas )


        toolbar =NavigationToolbar (event_canvas ,event_plot_tab )
        event_plot_layout .addWidget (toolbar )

        tab_widget .addTab (event_plot_tab ,"Event Data")


        segment_info_tab =QWidget ()
        segment_info_layout =QVBoxLayout (segment_info_tab )
        segment_info_text =QTextEdit ()
        segment_info_layout .addWidget (segment_info_text )
        tab_widget .addTab (segment_info_tab ,"Segment Info")


        event_analysis_tab =QWidget ()
        event_analysis_layout =QVBoxLayout (event_analysis_tab )
        event_analysis_text =QTextEdit ()
        event_analysis_layout .addWidget (event_analysis_text )
        tab_widget .addTab (event_analysis_tab ,"Event Analysis")

        def update_event_display (ec ):
            nonlocal event_counter 
            event_counter =ec 
            dialog .setWindowTitle (f"Event {event_counter } Details")

            event_key =f'EVENT_DATA_{event_counter }'
            segment_info_key =f'SEGMENT_INFO_{event_counter }'


            event_figure .clear ()
            ax =event_figure .add_subplot (111 )
            time_points =self .loaded_data [f'{event_key }_part_0']
            event_data =self .loaded_data [f'{event_key }_part_1']
            baseline =self .loaded_data [f'{event_key }_part_4']
            fitted_data =self .loaded_data [f'{event_key }_part_3']

            ax .plot (time_points ,event_data ,label ='Event Data')
            ax .plot (time_points ,baseline ,label ='Baseline',linestyle ='--')
            ax .plot (time_points ,fitted_data ,label ='Fitted Data',linestyle ='-.')
            ax .set_title (f"Event {event_counter } Data")
            ax .set_xlabel ("Time")
            ax .set_ylabel ("Amplitude")

            event_canvas .draw ()


            segment_info =""
            for key in self .loaded_data .keys ():
                if key .startswith (segment_info_key ):
                    value =self .loaded_data [key ]
                    segment_info +=f"{key .split ('_')[-1 ]}: {value }\n"
            segment_info_text .setText (segment_info )


            event_analysis_key =f'EVENT_ANALYSIS_{event_counter }'
            if event_analysis_key in self .loaded_data :
                event_analysis =self .loaded_data [event_analysis_key ]
                analysis_text ="Event Analysis:\n"
                for i ,value in enumerate (['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']):
                    analysis_text +=f"{value }: {event_analysis [i ]:.8f}\n"
                event_analysis_text .setText (analysis_text )


            prev_button .setEnabled (event_counter >0 )
            next_button .setEnabled (f'EVENT_DATA_{event_counter +1 }_part_0'in self .loaded_data )

        update_event_display (event_counter )

        def go_to_previous_event ():
            if event_counter >0 :
                update_event_display (event_counter -1 )

        def go_to_next_event ():
            if f'EVENT_DATA_{event_counter +1 }_part_0'in self .loaded_data :
                update_event_display (event_counter +1 )

        prev_button .clicked .connect (go_to_previous_event )
        next_button .clicked .connect (go_to_next_event )

        dialog .exec ()

    def refresh_raw_data (self ):
        if 'X'in self .loaded_data and isinstance (self .loaded_data ['X'],np .ndarray ):
            X_data =self .loaded_data ['X']
            requested_rows =self .row_spinner .value ()
            num_rows =min (requested_rows ,X_data .shape [0 ])

            self .raw_data_table .setRowCount (0 )
            for i in range (num_rows ):
                self .raw_data_table .insertRow (i )
                for j in range (X_data .shape [1 ]):
                    self .raw_data_table .setItem (i ,j ,QTableWidgetItem (f"{X_data [i ,j ]:.8f}"))

            self .raw_data_table .resizeColumnsToContents ()

            if num_rows <requested_rows :
                QMessageBox .information (self ,"Row Limit",f"Only {num_rows } rows available. Displaying all available rows.")

    def summarize_X_data (self ,X ):
        variables =['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']
        summary ="X data summary:\n"
        for i ,var in enumerate (variables ):
            col_data =X [:,i ]
            summary +=f"{var }: Mean={col_data .mean ():.8f}, Std={col_data .std ():.8f}, Min={col_data .min ():.8f}, Max={col_data .max ():.8f}\n"
        return summary 

    def display_event_data (self ):
        if 'events'in self .loaded_data :
            events =self .loaded_data ['events']
            for i ,event in enumerate (events ):
                row =self .data_table .rowCount ()
                self .data_table .insertRow (row )
                self .data_table .setItem (row ,0 ,QTableWidgetItem (f"Event {i }"))
                self .data_table .setItem (row ,1 ,QTableWidgetItem ("Event Data"))
                summary =f"Start: {event ['start_time']:.8f}, End: {event ['end_time']:.8f}, Duration: {event ['end_time']-event ['start_time']:.8f}"
                self .data_table .setItem (row ,2 ,QTableWidgetItem (summary ))

    def display_generic (self ):
        for key ,value in self .loaded_data .items ():
            row =self .data_table .rowCount ()
            self .data_table .insertRow (row )
            self .data_table .setItem (row ,0 ,QTableWidgetItem (str (key )))
            self .data_table .setItem (row ,1 ,QTableWidgetItem (str (type (value ))))
            if isinstance (value ,np .ndarray ):
                summary =f"Shape: {value .shape }"
                if value .dtype .kind in ['i','f']:
                    summary +=f", Mean: {value .mean ():.2f}, Std: {value .std ():.2f}"
                self .data_table .setItem (row ,2 ,QTableWidgetItem (summary ))
            else :
                self .data_table .setItem (row ,2 ,QTableWidgetItem (str (value )))



    def display_settings (self ):
        try :
            if self .loaded_data is not None and 'settings'in self .loaded_data :
                settings =self .loaded_data ['settings']


                if isinstance (settings ,np .ndarray ):
                    if settings .dtype ==object and len (settings )>0 :
                        settings =settings [0 ]
                    else :
                        settings =str (settings )

                try :

                    if isinstance (settings ,str ):
                        settings_dict =json .loads (settings )
                    elif isinstance (settings ,dict ):
                        settings_dict =settings 
                    else :
                        raise ValueError ("Settings data is not in a recognized format")

                    self .settings_table .clear ()
                    self .settings_table .setRowCount (0 )
                    self .settings_table .setColumnCount (2 )
                    self .settings_table .setHorizontalHeaderLabels (["Setting","Value"])

                    for key ,value in settings_dict .items ():
                        row =self .settings_table .rowCount ()
                        self .settings_table .insertRow (row )
                        self .settings_table .setItem (row ,0 ,QTableWidgetItem (str (key )))
                        self .settings_table .setItem (row ,1 ,QTableWidgetItem (str (value )))

                    self .settings_table .resizeColumnsToContents ()
                except json .JSONDecodeError :
                    print ("Error decoding settings JSON")
                    self .display_settings_as_string (settings )
                except ValueError as e :
                    print (f"Error processing settings: {str (e )}")
                    self .display_settings_as_string (settings )
            else :
                self .settings_table .clear ()
                self .settings_table .setRowCount (1 )
                self .settings_table .setColumnCount (1 )
                self .settings_table .setItem (0 ,0 ,QTableWidgetItem ("No settings data available"))
        except :
            pass 

    def display_settings_as_string (self ,settings ):
        self .settings_table .clear ()
        self .settings_table .setRowCount (1 )
        self .settings_table .setColumnCount (1 )
        self .settings_table .setItem (0 ,0 ,QTableWidgetItem (str (settings )))
        self .settings_table .resizeColumnsToContents ()

    def update_plot_options (self ):
        self .is_updating_plot_options =True 
        self .hide_all_plot_widgets ()

        self .plot_type_combo .clear ()
        self .show_plot_option ("plot_type")
        self .show_plot_option ("plot_file")
        self .plot_button .setVisible (True )

        if self .file_type is None :
            self .plot_type_combo .addItem ("No file loaded")
            self .plot_type_combo .setEnabled (False )
        else :
            self .plot_type_combo .setEnabled (True )
            if self .file_type in ['dataset','MLdataset']:
                self .plot_type_combo .addItems (["X Data Variable Distribution","X Data Variable Scatter"])
                self .update_dataset_options ()
            elif self .file_type in ['event_fitting','event_data']:
                self .plot_type_combo .addItems (["Individual Event","Multiple Events","Event Properties Histogram","Scatter Plot"])
                self .update_event_options ()

        self .on_plot_type_changed ()
        self .is_updating_plot_options =False 

    def show_plot_option (self ,option ):
        if self .plot_options_form is None :
            return 

        index =list (self .plot_options .keys ()).index (option )
        label_item =self .plot_options_form .itemAt (index ,QFormLayout .LabelRole )
        field_item =self .plot_options_form .itemAt (index ,QFormLayout .FieldRole )

        if label_item and label_item .widget ():
            label_item .widget ().setVisible (True )

        if field_item :
            if isinstance (field_item ,QLayoutItem )and field_item .widget ():
                field_item .widget ().setVisible (True )
            elif isinstance (field_item ,QLayout ):
                for i in range (field_item .count ()):
                    if field_item .itemAt (i )and field_item .itemAt (i ).widget ():
                        field_item .itemAt (i ).widget ().setVisible (True )


    def get_num_events (self ):
        if self .file_type =='event_fitting':

            event_numbers =set ()
            for key in self .loaded_data .keys ():
                if key .startswith ('EVENT_DATA_'):
                    parts =key .split ('_')
                    if len (parts )>2 and parts [2 ].isdigit ():
                        event_numbers .add (int (parts [2 ]))
            return len (event_numbers )
        elif self .file_type =='event_data'and 'events'in self .loaded_data :
            return len (self .loaded_data ['events'])
        return 0 

    def plot_data (self ):
        if self .loaded_data is None and not self .comparison_data :
            print ("No data loaded.")
            return 

        plot_type =self .plot_type_combo .currentText ()
        selected_file =self .plot_file_combo .currentText ()

        self .figure .clear ()
        ax =self .figure .add_subplot (111 )

        if selected_file =="Current File":
            data_to_plot ={"Current File":self .loaded_data }if self .loaded_data else self .comparison_data 
        else :
            data_to_plot ={selected_file :self .comparison_data [selected_file ]}

        try :
            if self .file_type in ['dataset','MLdataset']:
                self .plot_dataset_data (ax ,data_to_plot ,plot_type )
            elif self .file_type in ['event_fitting','event_data']:
                self .plot_event_data (ax ,data_to_plot ,plot_type )

            if plot_type !="Multiple Events"and ax .get_legend_handles_labels ()[0 ]:
                ax .legend ()

            self .canvas .draw ()
        except Exception as e :
            print (f"Error generating plot: {str (e )}")
            import traceback 
            traceback .print_exc ()

        QApplication .processEvents ()

    def plot_dataset_data (self ,ax ,data_to_plot ,plot_type ):
        if plot_type =="X Data Variable Distribution":
            self .plot_x_data_variable (ax ,data_to_plot )
        elif plot_type =="X Data Variable Scatter":
            self .plot_x_data_scatter (ax ,data_to_plot )

    def plot_event_data (self ,ax ,data_to_plot ,plot_type ):
        if plot_type =="Individual Event":
            centering =self .center_events_combo .currentText ()
            self .plot_single_event (ax ,data_to_plot ,centering )
        elif plot_type =="Multiple Events":
            centering =self .center_events_combo .currentText ()
            self .plot_multiple_events (ax ,data_to_plot ,centering )
        elif plot_type =="Event Properties Histogram":
            self .plot_event_properties_histogram (ax ,data_to_plot )
        elif plot_type =="Scatter Plot":
            self .plot_scatter (ax ,data_to_plot )



    def plot_x_data_distribution (self ,ax ):
        variable =self .x_variable_combo .currentText ()
        var_index =['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time'].index (variable )
        X_data =self .loaded_data ['X']
        variable_data =X_data [:,var_index ]
        ax .hist (variable_data ,bins =30 )
        ax .set_title (f"{variable } Distribution")
        ax .set_xlabel (variable )
        ax .set_ylabel ("Frequency")

    def plot_x_data_scatter (self ,ax ,data_to_plot ):
        x_variable =self .x_variable_combo .currentText ()
        y_variable =self .y_variable_combo .currentText ()

        if self .file_type =='MLdataset':
            x_index =self .ml_variables .index (x_variable )
            y_index =self .ml_variables .index (y_variable )
        else :
            variables =['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']
            x_index =variables .index (x_variable )
            y_index =variables .index (y_variable )

        for label ,data in data_to_plot .items ():
            if 'X'in data :
                X_data =data ['X']
                ax .scatter (X_data [:,x_index ],X_data [:,y_index ],label =label ,alpha =0.5 )

        ax .set_title (f"{y_variable } vs {x_variable }")
        ax .set_xlabel (x_variable )
        ax .set_ylabel (y_variable )


    def plot_single_event (self ,ax ,data_to_plot ,centering ):
        event_number =int (self .event_number_combo .currentText ().split ()[-1 ])
        for label ,data in data_to_plot .items ():
            if self .file_type =='event_fitting':
                event_key =f'EVENT_DATA_{event_number }'
                if f'{event_key }_part_0'not in data :
                    continue 
                time_points =data [f'{event_key }_part_0']
                event_data =data [f'{event_key }_part_1']
                baseline =data [f'{event_key }_part_4']
                fitted_data =data [f'{event_key }_part_3']

                ax .plot (time_points ,event_data ,label =f'{label } Event {event_number }')

                if self .plot_fitted_data_checkbox .isChecked ():
                    ax .plot (time_points ,fitted_data ,label =f'{label } Fitted Data',linestyle ='--')

                if self .plot_baseline_checkbox .isChecked ():
                    ax .plot (time_points ,baseline ,label =f'{label } Baseline',linestyle =':')

            elif 'events'in data :
                events =data ['events']
                if event_number >=len (events ):
                    continue 
                event =events [event_number ]
                time_points =np .arange (len (event ['event_data']))/data .get ('sampling_rate',1 )*1000 
                event_data =event ['event_data']
                ax .plot (time_points ,event_data ,label =f'{label } Event {event_number }')

        ax .set_title (f"Event {event_number } Data")
        ax .set_xlabel ("Time (ms)")
        ax .set_ylabel ("Amplitude")

    def plot_multiple_events (self ,ax ,data_to_plot ,centering ):
        start =self .event_range_start .value ()
        end =self .event_range_end .value ()
        colormap =plt .get_cmap ('viridis')

        plot_same_segments =self .same_segments_checkbox .isChecked ()
        selected_segments =None 
        if plot_same_segments and self .segments_number_combo .currentText ():
            try :
                selected_segments =int (self .segments_number_combo .currentText ())
            except ValueError :
                print ("Invalid segment number selected")

        for label ,data in data_to_plot .items ():
            events_to_plot =[]
            if self .file_type =='event_fitting':
                for event_number in range (start ,end +1 ):
                    event_key =f'EVENT_DATA_{event_number }'
                    if f'{event_key }_part_0'not in data :
                        continue 
                    time_points =data [f'{event_key }_part_0']
                    event_data =data [f'{event_key }_part_1']
                    baseline =data [f'{event_key }_part_4'][0 ]
                    segment_info_key =f'SEGMENT_INFO_{event_number }_number_of_segments'
                    num_segments =data .get (segment_info_key ,[0 ])[0 ]
                    if not plot_same_segments or (plot_same_segments and num_segments ==selected_segments ):
                        events_to_plot .append ((time_points ,event_data ,baseline ,num_segments ))
            elif 'events'in data :
                events =data ['events'][start :end +1 ]
                events_to_plot =[
                (np .arange (len (event ['event_data']))/data .get ('sampling_rate',1 )*1000 ,
                event ['event_data'],
                np .mean (event ['event_data'][:1 ]),
                event .get ('num_segments',0 ))
                for event in events 
                if not plot_same_segments or (plot_same_segments and event .get ('num_segments',0 )==selected_segments )
                ]

            for i ,(time_points ,event_data ,baseline ,num_segments )in enumerate (events_to_plot ):
                centered_time ,centered_data =self .center_event (time_points ,event_data ,centering )
                color =colormap (i /len (events_to_plot )if events_to_plot else 0 )
                ax .plot (centered_time ,centered_data -baseline ,color =color ,alpha =0.7 ,
                label =f'{label } Event {start +i } (Segments: {num_segments })')

        ax .set_title (f"Multiple Events{' (Same Segments)'if plot_same_segments else ''}")
        ax .set_xlabel ("Time (ms)")
        ax .set_ylabel ("Amplitude")
        if len (events_to_plot )<0 :
            ax .text (0.5 ,0.5 ,"No events match the current criteria",
            ha ='center',va ='center',transform =ax .transAxes )


    def center_event (self ,time_points ,event_data ,centering ):
        if centering =="Center on Minimum":
            center_index =np .argmin (event_data )
        elif centering =="Center on Maximum":
            center_index =np .argmax (event_data )
        else :
            center_index =len (event_data )//2 

        centered_time =time_points -time_points [center_index ]
        return centered_time ,event_data 

    def plot_segment_mean_differences (self ,ax ):
        event_number =int (self .event_number_combo .currentText ().split ()[-1 ])
        segment_mean_diffs =self .loaded_data [f'SEGMENT_INFO_{event_number }_segment_mean_diffs']
        ax .plot (segment_mean_diffs )
        ax .set_title (f"Event {event_number } Segment Mean Differences")
        ax .set_xlabel ("Segment")
        ax .set_ylabel ("Mean Difference")

    def plot_segment_widths (self ,ax ):
        event_number =int (self .event_number_combo .currentText ().split ()[-1 ])
        segment_widths =self .loaded_data [f'SEGMENT_INFO_{event_number }_segment_widths_time']
        ax .plot (segment_widths )
        ax .set_title (f"Event {event_number } Segment Widths")
        ax .set_xlabel ("Segment")
        ax .set_ylabel ("Width (time)")

    def plot_all_events (self ,ax ):
        events =self .loaded_data ['events']
        for event in events :
            event_data =event ['event_data']
            time_points =np .linspace (event ['start_time'],event ['end_time'],len (event_data ))
            ax .plot (time_points ,event_data )
        ax .set_title ("All Events")
        ax .set_xlabel ("Time")
        ax .set_ylabel ("Amplitude")

    def plot_event_duration_distribution (self ,ax ):
        events =self .loaded_data ['events']
        durations =[event ['end_time']-event ['start_time']for event in events ]
        ax .hist (durations ,bins =30 )
        ax .set_title ("Event Duration Distribution")
        ax .set_xlabel ("Duration")
        ax .set_ylabel ("Frequency")

    def plot_x_data_variable (self ,ax ,data_to_plot ):
        variable =self .x_variable_combo .currentText ()
        for label ,data in data_to_plot .items ():
            if 'X'in data :
                X_data =data ['X']
                if self .file_type =='MLdataset':
                    var_index =self .ml_variables .index (variable )
                else :
                    var_index =['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time'].index (variable )
                variable_data =X_data [:,var_index ]
                ax .hist (variable_data ,bins =30 ,alpha =0.5 ,label =label )

        ax .set_title (f"{variable } Distribution")
        ax .set_xlabel (variable )
        ax .set_ylabel ("Frequency")


    def plot_event_properties_histogram (self ,ax ,data_to_plot ):
        for label ,data in data_to_plot .items ():
            if 'events'in data :
                events =data ['events']
                durations =[event ['end_time']-event ['start_time']for event in events ]
                amplitudes =[np .min (event ['event_data'])for event in events ]
                ax .hist (durations ,bins =30 ,alpha =0.5 ,label =f'{label } Duration')
                ax .hist (amplitudes ,bins =30 ,alpha =0.5 ,label =f'{label } Amplitude')

        ax .set_title ("Event Properties Histogram")
        ax .set_xlabel ("Value")
        ax .set_ylabel ("Frequency")


    def plot_scatter (self ,ax ,data_to_plot ):
        for label ,data in data_to_plot .items ():
            if 'events'in data :
                events =data ['events']
                durations =[event ['end_time']-event ['start_time']for event in events ]
                amplitudes =[np .min (event ['event_data'])for event in events ]
                ax .scatter (durations ,amplitudes ,label =label ,alpha =0.5 )

        ax .set_title ("Event Duration vs Amplitude")
        ax .set_xlabel ("Duration (s)")
        ax .set_ylabel ("Amplitude")



    def add_filter (self ):
        filter_widget =QWidget ()
        filter_layout =QGridLayout (filter_widget )

        variable_label =QLabel ("Variable:")
        variable_combo_box =QComboBox ()
        variables =self .get_filter_variables ()
        variable_combo_box .addItems (variables )
        filter_layout .addWidget (variable_label ,0 ,0 )
        filter_layout .addWidget (variable_combo_box ,0 ,1 )

        min_value_label =QLabel ("Min Value:")
        min_value_spin_box =QDoubleSpinBox ()
        min_value_spin_box .setDecimals (7 )
        min_value_spin_box .setRange (-1e20 ,1e20 )
        min_value_spin_box .setStepType (QDoubleSpinBox .StepType .AdaptiveDecimalStepType )
        filter_layout .addWidget (min_value_label ,1 ,0 )
        filter_layout .addWidget (min_value_spin_box ,1 ,1 )

        max_value_label =QLabel ("Max Value:")
        max_value_spin_box =QDoubleSpinBox ()
        max_value_spin_box .setDecimals (7 )
        max_value_spin_box .setRange (-1e20 ,1e20 )
        max_value_spin_box .setStepType (QDoubleSpinBox .StepType .AdaptiveDecimalStepType )
        filter_layout .addWidget (max_value_label ,2 ,0 )
        filter_layout .addWidget (max_value_spin_box ,2 ,1 )

        remove_filter_button =QPushButton ("Remove")
        remove_filter_button .clicked .connect (lambda :self .remove_filter (filter_widget ))
        filter_layout .addWidget (remove_filter_button ,3 ,0 ,1 ,2 )

        self .filter_layout .addWidget (filter_widget )
        self .update_logic_combo_boxes ()

    def get_filter_variables (self ):
        if self .file_type =='event_fitting':
            return ['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']
        elif self .file_type =='MLdataset':
            return self .ml_variables 
        elif self .file_type =='dataset':
            return ['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']
        else :
            return []

    def update_logic_combo_boxes (self ):
        filter_count =self .filter_layout .count ()

        for i in range (filter_count -1 ):
            filter_widget =self .filter_layout .itemAt (i ).widget ()
            filter_layout =filter_widget .layout ()

            if filter_layout .rowCount ()==4 :
                logic_combo_box =QComboBox ()
                logic_combo_box .addItems (["AND","OR"])
                filter_layout .addWidget (QLabel ("Logic:"),4 ,0 )
                filter_layout .addWidget (logic_combo_box ,4 ,1 )
            elif i <filter_count -2 :
                logic_label =filter_layout .itemAtPosition (4 ,0 )
                if logic_label is None :
                    logic_combo_box =QComboBox ()
                    logic_combo_box .addItems (["AND","OR"])
                    filter_layout .addWidget (QLabel ("Logic:"),4 ,0 )
                    filter_layout .addWidget (logic_combo_box ,4 ,1 )
            else :
                logic_label =filter_layout .itemAtPosition (4 ,0 )
                if logic_label :
                    filter_layout .removeItem (filter_layout .itemAtPosition (4 ,0 ))
                    filter_layout .removeItem (filter_layout .itemAtPosition (4 ,1 ))
                    logic_label .widget ().deleteLater ()
                    filter_layout .itemAtPosition (4 ,1 ).widget ().deleteLater ()

    def remove_filter (self ,filter_widget ):
        self .filter_layout .removeWidget (filter_widget )
        filter_widget .deleteLater ()
        self .update_logic_combo_boxes ()

    def apply_filters (self ):
        if self .loaded_data is None :
            QMessageBox .warning (self ,"Warning","No data loaded to filter.")
            return 

        mask =np .ones (self .get_data_length (),dtype =bool )

        for i in range (self .filter_layout .count ()):
            filter_widget =self .filter_layout .itemAt (i ).widget ()
            filter_layout =filter_widget .layout ()

            variable =filter_layout .itemAtPosition (0 ,1 ).widget ().currentText ()
            min_value =filter_layout .itemAtPosition (1 ,1 ).widget ().value ()
            max_value =filter_layout .itemAtPosition (2 ,1 ).widget ().value ()

            try :
                variable_values =self .get_variable_values (variable )
                condition =(variable_values >=min_value )&(variable_values <=max_value )

                if i ==0 :
                    mask =condition 
                else :
                    logic_combo =filter_layout .itemAtPosition (4 ,1 )
                    if logic_combo :
                        logic =logic_combo .widget ().currentText ()
                        if logic =="AND":
                            mask &=condition 
                        else :
                            mask |=condition 
                    else :
                        mask &=condition 
            except ValueError as e :
                QMessageBox .warning (self ,"Filter Error",f"Error applying filter for variable '{variable }': {str (e )}")
                return 

        self .apply_mask (mask )
        self .display_data ()
        QMessageBox .information (self ,"Filter Applied",f"Filtered data. {np .sum (mask )} items remaining.")

    def get_data_length (self ):
        if self .file_type =='event_fitting':
            return len ([key for key in self .loaded_data .keys ()if key .startswith ('EVENT_DATA_')])
        elif self .file_type in ['dataset','MLdataset']:
            return len (self .loaded_data ['X'])
        else :
            return 0 

    def get_variable_values (self ,variable ):
        if self .file_type =='event_fitting':
            return np .array ([self .loaded_data [f'EVENT_ANALYSIS_{i }'][self .get_variable_index (variable )]
            for i in range (self .get_data_length ())])
        elif self .file_type in ['dataset','MLdataset']:
            return self .loaded_data ['X'][:,self .get_variable_index (variable )]

    def get_variable_index (self ,variable ):
        if self .file_type =='MLdataset':
            return self .ml_variables .index (variable )
        elif self .file_type in ['dataset','event_fitting']:
            variables =['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']
            return variables .index (variable )
        else :
            raise ValueError (f"Unsupported file type: {self .file_type }")

    def apply_mask (self ,mask ):
        if self .file_type =='event_fitting':
            self .loaded_data ={k :v for k ,v in self .loaded_data .items ()
            if not k .startswith ('EVENT_')or int (k .split ('_')[2 ])in np .where (mask )[0 ]}
        elif self .file_type in ['dataset','MLdataset']:
            self .loaded_data ['X']=self .loaded_data ['X'][mask ]

    def save_filtered_data (self ):
        if self .loaded_data is None :
            QMessageBox .warning (self ,"Warning","No data loaded to save.")
            return 

        file_path ,_ =QFileDialog .getSaveFileName (self ,"Save Filtered Data","","NPZ Files (*.npz)")
        if file_path :
            try :
                np .savez_compressed (file_path ,**self .loaded_data )
                QMessageBox .information (self ,"Save Successful",f"Filtered data saved to {file_path }")
            except Exception as e :
                QMessageBox .critical (self ,"Save Failed",f"Failed to save filtered data: {str (e )}")

    def reset_filter (self ):
        if hasattr (self ,'original_data'):
            self .loaded_data =self .original_data .copy ()
            self .display_data ()
            QMessageBox .information (self ,"Filter Reset","Data reset to original state.")
        else :
            QMessageBox .warning (self ,"Warning","No original data available to reset to.")

    def export_to_npz (self ):
        if self .loaded_data is None :
            QMessageBox .warning (self ,"Warning","No data loaded to export.")
            return 

        file_path ,_ =QFileDialog .getSaveFileName (self ,"Save NPZ File","","NPZ Files (*.npz)")
        if file_path :
            try :
                np .savez_compressed (file_path ,**self .loaded_data )
                QMessageBox .information (self ,"Export Successful",f"Data exported to {file_path }")
            except Exception as e :
                QMessageBox .critical (self ,"Export Failed",f"Failed to export data: {str (e )}")

    def export_to_csv (self ):
        if self .loaded_data is None or 'events'not in self .loaded_data :
            QMessageBox .warning (self ,"Warning","No event data loaded to export.")
            return 

        file_path ,_ =QFileDialog .getSaveFileName (self ,"Save CSV File","","CSV Files (*.csv)")
        if file_path :
            try :
                events =self .loaded_data ['events']
                with open (file_path ,'w',newline ='')as csvfile :
                    writer =csv .writer (csvfile )
                    writer .writerow (['Event ID','Start Time','End Time','Duration','Min Amplitude','Max Amplitude'])

                    for i ,event in enumerate (events ):
                        start_time =event ['start_time']
                        end_time =event ['end_time']
                        duration =end_time -start_time 
                        min_amplitude =np .min (event ['event_data'])
                        max_amplitude =np .max (event ['event_data'])

                        writer .writerow ([i ,start_time ,end_time ,duration ,min_amplitude ,max_amplitude ])

                QMessageBox .information (self ,"Export Successful",f"Event data exported to {file_path }")
            except Exception as e :
                QMessageBox .critical (self ,"Export Failed",f"Failed to export data: {str (e )}")




if __name__ =="__main__":
    app =QApplication (sys .argv )
    app .setStyle (QStyleFactory .create ('Fusion'))

    palette =QPalette ()
    palette .setColor (QPalette .ColorRole .Window ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .WindowText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Base ,QColor (25 ,25 ,25 ))
    palette .setColor (QPalette .ColorRole .AlternateBase ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .ToolTipBase ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .ToolTipText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Text ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Button ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .ButtonText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .BrightText ,Qt .GlobalColor .red )
    palette .setColor (QPalette .ColorRole .Link ,QColor (42 ,130 ,218 ))
    palette .setColor (QPalette .ColorRole .Highlight ,QColor (42 ,130 ,218 ))
    palette .setColor (QPalette .ColorRole .HighlightedText ,Qt .GlobalColor .black )
    app .setPalette (palette )
    window =SDDatabaseViewer ()
    window .showMaximized ()
    sys .exit (app .exec ())