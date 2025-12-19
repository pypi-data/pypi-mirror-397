import sys 
from PySide6 .QtWidgets import QApplication ,QMainWindow ,QWidget ,QHBoxLayout ,QVBoxLayout ,QPushButton ,QCheckBox ,QListWidget ,QLabel ,QFileDialog ,QLineEdit ,QMessageBox ,QListWidgetItem ,QSplitter ,QGroupBox ,QFormLayout ,QComboBox ,QSpinBox ,QStyleFactory ,QTabWidget ,QScrollArea ,QGridLayout ,QComboBox ,QInputDialog 
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QPalette ,QColor 
import os 
import numpy as np 
from neo .rawio import AxonRawIO 
from scipy .ndimage import uniform_filter1d 
import matplotlib 
from matplotlib .backends .backend_qtagg import FigureCanvasQTAgg ,NavigationToolbar2QT 
from matplotlib .figure import Figure 
import h5py 
from scipy .signal import butter ,bessel ,cheby1 ,cheby2 ,ellip ,firwin ,lfilter ,sosfilt ,sosfilt_zi 
from PySide6 .QtWidgets import QProgressDialog 
from PySide6 .QtCore import Qt ,QSize 
from matplotlib .widgets import SpanSelector 
from concurrent .futures import ThreadPoolExecutor 
matplotlib .use ('Qt5Agg')
import math 
import struct 
import struct 

class MplCanvas (FigureCanvasQTAgg ):
    def __init__ (self ,parent =None ,width =5 ,height =4 ,dpi =100 ):
        fig =Figure (figsize =(width ,height ),dpi =dpi )
        self .axes =fig .add_subplot (111 )
        fig .tight_layout ()
        super ().__init__ (fig )


def load_dtlg_file (file_path ):
    with open (file_path ,'rb')as f :

        dtlg_format =struct .unpack ('>I',f .read (4 ))[0 ]
        if dtlg_format !=1146375239 :
            print ("Not a valid DTLG file")
            return None ,None ,None 


        f .seek (4 )
        version =struct .unpack ('B',f .read (1 ))[0 ]



        if version not in [7 ,8 ]:
            print (f"Unsupported version: {version }")
            return None ,None ,None 


        data =None 
        sampling_rate =None 
        freqver =0 

        if version ==8 :
            f .seek (10 )
            freqver =struct .unpack ('>H',f .read (2 ))[0 ]
            records =freqver 

            bof_offset =602 
            timestep_offset =590 
            f .seek (594 )
            unique_id =struct .unpack ('>I',f .read (4 ))[0 ]
            record_size =struct .unpack ('>I',f .read (4 ))[0 ]

            f .seek (594 )
            unique_id2 =struct .unpack ('>Q',f .read (8 ))[0 ]


            endrecordone =bof_offset +record_size *8 
            f .seek (endrecordone )
            while struct .unpack ('>Q',f .read (8 ))[0 ]!=unique_id2 :
                f .seek (-7 ,1 )
            header1size =f .tell ()-endrecordone 

            f .seek (record_size *8 ,1 )
            position2ini =f .tell ()
            while struct .unpack ('>Q',f .read (8 ))[0 ]!=unique_id2 :
                f .seek (-7 ,1 )
            header2size =f .tell ()-position2ini 

            magicnumber =header1size +header2size 
            voltagerecsize =record_size *8 +magicnumber 

            data =np .zeros (records *record_size )
            if freqver ==16 :
                header_offset =42 

        elif version ==7 :
            freqver =16 
            records =freqver 
            bof_offset =720 
            header_offset =36 
            timestep_offset =708 
            record_size =39999 
            data =np .zeros (640000 )

        if timestep_offset !=0 :
            f .seek (timestep_offset )
            timestep =struct .unpack ('>d',f .read (8 ))[0 ]
            sampling_rate =1 /timestep 

            f .seek (0 )

            if freqver ==16 and version ==7 :
                f .seek (bof_offset )
                Ain =np .frombuffer (f .read (),dtype ='>d')
                record_number =range (1 ,records +1 )
                record_start =80000 *(np .array (record_number )-1 )+(np .array (record_number )-1 )*header_offset 
                record_end =record_start +record_size 
                data =np .concatenate ([Ain [start :end ]for start ,end in zip (record_start ,record_end )])
            else :
                record_number =range (1 ,freqver +1 )
                record_start =record_size *(np .array (record_number )-1 )
                record_end =record_start +record_size 
                f .seek (bof_offset )

                total_data =[]
                for i in range (freqver ):
                    chunk =np .frombuffer (f .read (record_size *8 ),dtype ='>d')
                    total_data .append (chunk )
                    if i !=freqver -1 :
                        f .seek (voltagerecsize ,1 )

                data =np .concatenate (total_data )

            return data ,sampling_rate ,np .arange (len (data ))/sampling_rate 
        else :
            print ("Timestep offset is 0")
            return None ,None ,None 

    return None ,None ,None 

def load_abf_file (file_path ):

    raw_io =AxonRawIO (filename =file_path )


    raw_io .parse_header ()


    channel_index =0 


    signal_size =raw_io .get_signal_size (block_index =0 ,seg_index =0 )



    data =raw_io .get_analogsignal_chunk (block_index =0 ,seg_index =0 ,i_start =0 ,i_stop =signal_size ,channel_indexes =[channel_index ])


    data =raw_io .rescale_signal_raw_to_float (data ,dtype ='float64',channel_indexes =[channel_index ]).flatten ()


    sampling_rate =raw_io .get_signal_sampling_rate ()


    time =np .arange (len (data ))/sampling_rate 

    return data ,sampling_rate ,time 

def load_hdf5_file (file_path ):
    with h5py .File (file_path ,'r')as f :
        selected_data =f ['selected_data'][()]
        sampling_rate =f .attrs ['sampling_rate']
        time =np .arange (len (selected_data ))/sampling_rate 
    return selected_data ,sampling_rate ,time 

def calculate_rolling_stats (data ,sampling_rate ,avg_window_size_in_ms ):
    avg_window_size_samples =int ((avg_window_size_in_ms /1000 )*sampling_rate )
    if avg_window_size_samples <1 :
        return data 
    return uniform_filter1d (data ,size =avg_window_size_samples )


class Settings :
    def __init__ (self ):
        self .calculate_avg =False 
        self .avg_window_size =0 
        self .use_threshold =False 
        self .threshold_value =0 
        self .threshold_percentage =75 
        self .use_segments =False 
        self .segments =[]

    def __eq__ (self ,other ):
        if not isinstance (other ,Settings ):
            return NotImplemented 
        return (self .calculate_avg ==other .calculate_avg and 
        self .avg_window_size ==other .avg_window_size and 
        self .use_threshold ==other .use_threshold and 
        self .threshold_value ==other .threshold_value and 
        self .threshold_percentage ==other .threshold_percentage and 
        self .use_segments ==other .use_segments and 
        self .segments ==other .segments )

class PlotData :
    def __init__ (self ,file_path ,data ,unfiltered_data ,sampling_rate ,time ):
        self .file_path =file_path 
        self .data =data 
        self .unfiltered_data =unfiltered_data 
        self .sampling_rate =sampling_rate 
        self .time =time 
        self .mean_value =np .mean (data )
        self .settings ={
        'calculate_avg':False ,
        'avg_window_size':10 ,
        'use_threshold':False ,
        'threshold_value':self .mean_value ,
        'threshold_percentage':75 ,
        'use_segments':False ,
        'segments':[],
        'apply_baseline':False ,
        'baseline_window_size':5 ,
        }
        self .baseline_subtracted_data =None 
        self .baseline_subtracted_unfiltered_data =None 
        self .original_settings =self .settings .copy ()



        self .settings ['apply_baseline']=False 
        self .settings ['baseline_window_size']=5 
        self .baseline_subtracted_data =None 
        self .baseline_subtracted_unfiltered_data =None 



class SegmentWidget (QWidget ):
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        layout =QHBoxLayout ()
        self .setLayout (layout )

        self .start_label =QLabel ("Start (s):")
        self .start_input =QLineEdit ()
        self .end_label =QLabel ("End (s):")
        self .end_input =QLineEdit ()
        self .add_button =QPushButton ("Add Segment")
        self .apply_all_checkbox =QCheckBox ("Apply to All Plots")

        layout .addWidget (self .start_label )
        layout .addWidget (self .start_input )
        layout .addWidget (self .end_label )
        layout .addWidget (self .end_input )
        layout .addWidget (self .add_button )
        layout .addWidget (self .apply_all_checkbox )


class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD ABF File Plotter and Selector App")
        self .setGeometry (100 ,100 ,1200 ,800 )

        self .plot_data_dict ={}
        self .current_file_path =None 
        self .global_settings =Settings ()

        main_splitter =QSplitter (Qt .Orientation .Horizontal )

        left_widget =QWidget ()
        left_layout =QVBoxLayout ()
        left_widget .setLayout (left_layout )

        right_widget =QWidget ()
        right_layout =QVBoxLayout ()
        right_widget .setLayout (right_layout )

        main_splitter .addWidget (left_widget )
        main_splitter .addWidget (right_widget )
        main_splitter .setSizes ([300 ,900 ])

        self .setCentralWidget (main_splitter )


        self .app_name_label =QLabel ("SD ABF File Plotter and Selector App")
        self .app_name_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .app_name_label .setStyleSheet ("font-size: 22px; font-weight: bold;")
        self .email_label =QLabel ("shankar.dutt@anu.edu.au")
        self .email_label .setAlignment (Qt .AlignmentFlag .AlignCenter )

        self .select_folder_btn =QPushButton ("Select Folder")
        self .select_folder_btn .clicked .connect (self .select_folder )

        self .include_subfolders_chk =QCheckBox ("Include Subfolders")

        self .files_list_widget =QListWidget ()
        self .files_list_widget .setSelectionMode (QListWidget .SelectionMode .MultiSelection )

        self .folder_path_label =QLabel (" ")
        self .folder_path_label .setWordWrap (True )

        self .plot_multiple_files_chk =QCheckBox ("Plot multiple files")
        self .plot_multiple_files_chk .stateChanged .connect (self .toggle_plot_multiple_files )

        nth_element_layout =QHBoxLayout ()
        self .nth_element_label =QLabel ("Plot nth element:")
        self .nth_element_spinbox =QSpinBox ()
        self .nth_element_spinbox .setMinimum (1 )
        self .nth_element_spinbox .setMaximum (1000 )
        self .nth_element_spinbox .setValue (1 )
        nth_element_layout .addWidget (self .nth_element_label )
        nth_element_layout .addWidget (self .nth_element_spinbox )

        self .low_pass_filter_chk =QCheckBox ("Apply Low Pass Filter")
        self .low_pass_filter_chk .stateChanged .connect (self .toggle_low_pass_filter )

        self .filter_type_label =QLabel ("Filter Type:")
        self .filter_type_dropdown =QComboBox ()
        self .filter_type_dropdown .addItems (["Butterworth","Bessel","Chebyshev I","Chebyshev II","Elliptic","FIR","IIR"])
        self .filter_type_dropdown .setEnabled (False )

        self .cutoff_frequency_label =QLabel ("Cutoff Frequency (kHz):")
        self .cutoff_frequency_spinbox =QSpinBox ()
        self .cutoff_frequency_spinbox .setRange (1 ,1000 )
        self .cutoff_frequency_spinbox .setValue (10 )
        self .cutoff_frequency_spinbox .setEnabled (False )

        self .plot_btn =QPushButton ("Plot Selected File(s)")
        self .plot_btn .clicked .connect (self .plot_selected_files )

        left_layout .addWidget (self .app_name_label )
        left_layout .addWidget (self .email_label )
        left_layout .addWidget (self .select_folder_btn )
        left_layout .addWidget (self .include_subfolders_chk )
        left_layout .addWidget (self .files_list_widget )
        left_layout .addWidget (self .folder_path_label )
        left_layout .addWidget (self .plot_multiple_files_chk )
        left_layout .addLayout (nth_element_layout )
        left_layout .addWidget (self .low_pass_filter_chk )
        left_layout .addWidget (self .filter_type_label )
        left_layout .addWidget (self .filter_type_dropdown )
        left_layout .addWidget (self .cutoff_frequency_label )
        left_layout .addWidget (self .cutoff_frequency_spinbox )
        left_layout .addWidget (self .plot_btn )


        self .plot_scroll_area =QScrollArea ()
        self .plot_scroll_area .setWidgetResizable (True )
        self .plot_widget =QWidget ()
        self .plot_layout =QGridLayout ()
        self .plot_widget .setLayout (self .plot_layout )
        self .plot_scroll_area .setWidget (self .plot_widget )
        right_layout .addWidget (self .plot_scroll_area ,7 )


        self .plot_selection_dropdown =QComboBox ()
        self .plot_selection_dropdown .currentIndexChanged .connect (self .on_plot_selection_changed )
        right_layout .addWidget (self .plot_selection_dropdown )


        self .control_tabs =QTabWidget ()
        right_layout .addWidget (self .control_tabs ,3 )


        self .avg_tab =QWidget ()
        self .avg_layout =QVBoxLayout ()
        self .avg_tab .setLayout (self .avg_layout )
        self .calculate_avg_chk =QCheckBox ("Calculate and Plot Avg")
        self .avg_window_size_input =QLineEdit ("10")
        self .avg_layout .addWidget (self .calculate_avg_chk )
        self .avg_layout .addWidget (QLabel ("Avg Window Size (ms):"))
        self .avg_layout .addWidget (self .avg_window_size_input )
        self .control_tabs .addTab (self .avg_tab ,"Average")


        self .threshold_tab =QWidget ()
        self .threshold_layout =QVBoxLayout ()
        self .threshold_tab .setLayout (self .threshold_layout )
        self .threshold_chk =QCheckBox ("Select Regions within Threshold")
        self .threshold_value_input =QSpinBox ()
        self .threshold_value_input .setRange (0 ,1000000 )
        self .threshold_percentage_input =QSpinBox ()
        self .threshold_percentage_input .setRange (0 ,100 )
        self .threshold_percentage_input .setValue (75 )
        self .threshold_layout .addWidget (self .threshold_chk )
        self .threshold_layout .addWidget (QLabel ("Value for selecting regions (pA):"))
        self .threshold_layout .addWidget (self .threshold_value_input )
        self .threshold_layout .addWidget (QLabel ("Threshold (%):"))
        self .threshold_layout .addWidget (self .threshold_percentage_input )
        self .control_tabs .addTab (self .threshold_tab ,"Threshold")


        self .segments_tab =QWidget ()
        self .segments_layout =QVBoxLayout ()
        self .segments_tab .setLayout (self .segments_layout )
        self .select_segments_chk =QCheckBox ("Select Segments")
        self .segment_list =QListWidget ()
        self .add_segment_btn =QPushButton ("Add Segment")
        self .delete_segment_btn =QPushButton ("Delete Segment")
        self .segments_layout .addWidget (self .select_segments_chk )
        self .segments_layout .addWidget (self .segment_list )
        self .segments_layout .addWidget (self .add_segment_btn )
        self .segments_layout .addWidget (self .delete_segment_btn )
        self .control_tabs .addTab (self .segments_tab ,"Segments")



        self .baseline_tab =QWidget ()
        self .baseline_layout =QVBoxLayout ()
        self .baseline_tab .setLayout (self .baseline_layout )

        self .baseline_chk =QCheckBox ("Apply Baseline Subtraction")
        self .baseline_window_size_label =QLabel ("Baseline Window Size (ms):")
        self .baseline_window_size_input =QLineEdit ("5")

        self .baseline_layout .addWidget (self .baseline_chk )
        self .baseline_layout .addWidget (self .baseline_window_size_label )
        self .baseline_layout .addWidget (self .baseline_window_size_input )

        self .control_tabs .addTab (self .baseline_tab ,"Baseline")


        self .baseline_chk .stateChanged .connect (self .update_baseline_settings )
        self .baseline_window_size_input .editingFinished .connect (self .update_baseline_settings )



        self .global_settings_chk =QCheckBox ("Apply settings to all plots")
        right_layout .addWidget (self .global_settings_chk )


        self .save_btn =QPushButton ("Save Selected Data")
        self .save_btn .clicked .connect (self .save_selected_data )
        right_layout .addWidget (self .save_btn )


        self .calculate_avg_chk .stateChanged .connect (self .update_avg_settings )
        self .avg_window_size_input .editingFinished .connect (self .update_avg_settings )
        self .threshold_chk .stateChanged .connect (self .update_threshold_settings )
        self .threshold_value_input .valueChanged .connect (self .update_threshold_settings )
        self .threshold_percentage_input .valueChanged .connect (self .update_threshold_settings )
        self .select_segments_chk .stateChanged .connect (self .update_segment_settings )
        self .add_segment_btn .clicked .connect (self .add_segment )
        self .delete_segment_btn .clicked .connect (self .delete_segment )


        self .update_plot_btn =QPushButton ("Update Plot")
        self .update_plot_btn .clicked .connect (self .apply_settings_and_update_plots )
        right_layout .addWidget (self .update_plot_btn )

    def on_plot_selection_changed (self ,index ):
        if 0 <=index <self .plot_selection_dropdown .count ():
            self .current_file_path =self .plot_selection_dropdown .itemData (index )
            self .update_ui_from_settings ()

    def apply_settings_and_update_plots (self ):
        self .update_settings_from_ui ()
        if self .global_settings_chk .isChecked ():
            current_settings =self .plot_data_dict [self .current_file_path ].settings 
            for plot_data in self .plot_data_dict .values ():
                plot_data .settings =current_settings .copy ()

        for file_path ,plot_data in self .plot_data_dict .items ():
            if plot_data .settings !=plot_data .original_settings :
                self .apply_baseline_subtraction (plot_data )
                self .update_single_plot (file_path )
                plot_data .original_settings =plot_data .settings .copy ()


    def toggle_low_pass_filter (self ,state ):
        self .filter_type_dropdown .setEnabled (state ==Qt .CheckState .Checked .value )
        self .cutoff_frequency_spinbox .setEnabled (state ==Qt .CheckState .Checked .value )

    def toggle_plot_multiple_files (self ,state ):

        self .files_list_widget .setSelectionMode (
        QListWidget .SelectionMode .MultiSelection if state ==Qt .CheckState .Checked .value 
        else QListWidget .SelectionMode .SingleSelection 
        )

    def update_baseline_settings (self ):
        self .update_settings_from_ui ()

    def finish_baseline_selection (self ,span_selector ):
        span_selector .disconnect_events ()
        self .select_baseline_btn .setText ("Select Baseline Region")
        self .select_baseline_btn .clicked .disconnect ()
        self .select_baseline_btn .clicked .connect (self .select_baseline_region )

    def apply_baseline_subtraction (self ,plot_data ):
        if not plot_data .settings ['apply_baseline']:
            plot_data .baseline_subtracted_data =None 
            plot_data .baseline_subtracted_unfiltered_data =None 
            return 


        window_size =int ((plot_data .settings ['baseline_window_size']/1000 )*plot_data .sampling_rate )


        plot_data .baseline_subtracted_data =np .zeros_like (plot_data .data )
        plot_data .baseline_subtracted_unfiltered_data =np .zeros_like (plot_data .unfiltered_data )


        for i in range (0 ,len (plot_data .data ),window_size ):
            end =min (i +window_size ,len (plot_data .data ))


            baseline_mean =np .mean (plot_data .data [i :end ])
            baseline_mean_unfiltered =np .mean (plot_data .unfiltered_data [i :end ])


            plot_data .baseline_subtracted_data [i :end ]=plot_data .data [i :end ]-baseline_mean 
            plot_data .baseline_subtracted_unfiltered_data [i :end ]=plot_data .unfiltered_data [i :end ]-baseline_mean_unfiltered 

    def get_current_figure (self ):
        index =list (self .plot_data_dict .keys ()).index (self .current_file_path )
        plot_widget =self .plot_layout .itemAt (index ).widget ()
        canvas =plot_widget .layout ().itemAt (0 ).widget ()
        return canvas .figure 

    def select_folder (self ):
        options =QFileDialog .Option .ShowDirsOnly 
        directory =QFileDialog .getExistingDirectory (self ,"Select Folder","",options =options )
        if directory :
            self .folder_path_label .setText (f"Selected folder: {directory }")
            self .populate_file_list (directory ,self .include_subfolders_chk .isChecked ())

    def apply_low_pass_filter (self ,data ,cutoff_frequency ,type ,sampling_rate ):
        if type =='Butterworth':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =butter (N =8 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='Bessel':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =bessel (N =8 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='Chebyshev I':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =cheby1 (N =8 ,rp =0.1 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='Chebyshev II':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =cheby2 (N =8 ,rs =40 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='Elliptic':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =ellip (N =8 ,rp =0.1 ,rs =40 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='FIR':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            taps =firwin (101 ,cutoff )
            filtered_data =lfilter (taps ,1 ,data )
            return filtered_data 
        elif type =='IIR':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            b ,a =butter (N =8 ,Wn =cutoff ,btype ='low',analog =False )
            filtered_data =lfilter (b ,a ,data )
            return filtered_data 

    def update_settings (self ):
        if self .global_settings_chk .isChecked ():
            settings =self .global_settings 
        elif self .current_file_path :
            settings =self .plot_data_dict [self .current_file_path ].settings 
        else :
            return 

        new_settings =Settings ()
        new_settings .calculate_avg =self .calculate_avg_chk .isChecked ()
        new_settings .avg_window_size =float (self .avg_window_size_input .text ())
        new_settings .use_threshold =self .threshold_chk .isChecked ()
        new_settings .threshold_value =self .threshold_value_input .value ()/1000 
        new_settings .threshold_percentage =self .threshold_percentage_input .value ()
        new_settings .use_segments =self .select_segments_chk .isChecked ()
        new_settings .segments =self .get_segments_from_list ()

        if self .global_settings_chk .isChecked ():
            self .global_settings =new_settings 
        else :
            self .plot_data_dict [self .current_file_path ].settings =new_settings 


    def update_ui_from_settings (self ):
        if not self .current_file_path :
            return 
        plot_data =self .plot_data_dict [self .current_file_path ]
        settings =plot_data .settings 


        self .calculate_avg_chk .setChecked (settings .get ('calculate_avg',False ))
        self .avg_window_size_input .setText (str (settings .get ('avg_window_size',10 )))
        self .threshold_chk .setChecked (settings .get ('use_threshold',False ))
        self .threshold_value_input .setValue (int (settings .get ('threshold_value',0 )*1000 ))
        self .threshold_percentage_input .setValue (settings .get ('threshold_percentage',75 ))


        self .segment_list .clear ()


        if 'segments'in settings and settings ['segments']:
            for start ,end in settings ['segments']:
                self .segment_list .addItem (f"{start :.2f} - {end :.2f}")
            self .select_segments_chk .setChecked (True )
        else :
            self .select_segments_chk .setChecked (False )


        settings ['use_segments']=self .select_segments_chk .isChecked ()

        self .baseline_chk .setChecked (settings .get ('apply_baseline',False ))
        self .baseline_window_size_input .setText (str (settings .get ('baseline_window_size',5 )))


    def update_settings_from_ui (self ):
        if not self .current_file_path :
            return 
        plot_data =self .plot_data_dict [self .current_file_path ]
        settings =plot_data .settings 
        settings ['calculate_avg']=self .calculate_avg_chk .isChecked ()
        settings ['avg_window_size']=float (self .avg_window_size_input .text ())
        settings ['use_threshold']=self .threshold_chk .isChecked ()
        settings ['threshold_value']=self .threshold_value_input .value ()/1000 
        settings ['threshold_percentage']=self .threshold_percentage_input .value ()
        settings ['use_segments']=self .select_segments_chk .isChecked ()
        settings ['segments']=self .get_segments_from_list ()
        settings ['apply_baseline']=self .baseline_chk .isChecked ()
        settings ['baseline_window_size']=float (self .baseline_window_size_input .text ())


    def populate_file_list (self ,directory ,include_subfolders ):
        self .files_list_widget .clear ()
        self .plot_data_dict .clear ()
        file_list =[]

        for root ,dirs ,files in os .walk (directory ):
            for file in files :
                if file .endswith ('.abf')or file .endswith ('.hdf5')or file .endswith ('.h5')or file .endswith ('.dtlg'):
                    rel_path =os .path .relpath (os .path .join (root ,file ),start =directory )
                    full_path =os .path .join (root ,file )
                    file_list .append ((rel_path ,full_path ))

            if not include_subfolders :
                break 

        file_list .sort (key =lambda x :x [0 ].lower ())

        for rel_path ,full_path in file_list :
            item =QListWidgetItem (rel_path )
            item .setData (Qt .ItemDataRole .UserRole ,full_path )
            self .files_list_widget .addItem (item )

    def plot_selected_files (self ):
        selected_items =self .files_list_widget .selectedItems ()
        if not selected_items :
            return 

        self .plot_data_dict .clear ()
        self .clear_plot_layout ()

        if not self .plot_multiple_files_chk .isChecked ():
            selected_items =[selected_items [0 ]]

        total_steps =len (selected_items )*2 
        progress =QProgressDialog ("Processing files...","Cancel",0 ,total_steps ,self )
        progress .setWindowModality (Qt .WindowModal )
        progress .setWindowTitle ("Please Wait")
        progress .setMinimumDuration (0 )

        current_step =0 


        for item in selected_items :
            if progress .wasCanceled ():
                return 
            file_path =item .data (Qt .ItemDataRole .UserRole )
            progress .setLabelText (f"Loading {os .path .basename (file_path )}...")
            try :
                data ,unfiltered_data ,sampling_rate ,time =self .load_file (file_path )
                plot_data =PlotData (file_path ,data ,unfiltered_data ,sampling_rate ,time )
                self .plot_data_dict [file_path ]=plot_data 
            except Exception as e :
                QMessageBox .warning (self ,"Error",str (e ))
            current_step +=1 
            progress .setValue (current_step )
            QApplication .processEvents ()


        num_plots =len (self .plot_data_dict )
        cols =math .ceil (math .sqrt (num_plots ))
        rows =math .ceil (num_plots /cols )

        for i ,(file_path ,plot_data )in enumerate (self .plot_data_dict .items ()):
            if progress .wasCanceled ():
                break 
            progress .setLabelText (f"Plotting {os .path .basename (file_path )}...")

            row =i //cols 
            col =i %cols 


            plot_widget =QWidget ()
            plot_layout =QVBoxLayout (plot_widget )
            plot_layout .setSpacing (0 )
            plot_layout .setContentsMargins (0 ,0 ,0 ,0 )

            figure =Figure (figsize =(5 ,3 ),dpi =100 )
            canvas =FigureCanvasQTAgg (figure )
            ax =figure .add_subplot (111 )

            self .plot_data (ax ,plot_data )


            toolbar =NavigationToolbar2QT (canvas ,plot_widget )
            toolbar .setIconSize (QSize (16 ,16 ))
            toolbar .setStyleSheet ("""
                QToolBar { border: 0px }
                QToolButton { border: 0px; padding: 1px; }
            """)

            plot_layout .addWidget (canvas )
            plot_layout .addWidget (toolbar )

            self .plot_layout .addWidget (plot_widget ,row ,col )

            current_step +=1 
            progress .setValue (current_step )
            QApplication .processEvents ()

        progress .close ()


        self .plot_selection_dropdown .clear ()
        for file_path in self .plot_data_dict .keys ():
            self .plot_selection_dropdown .addItem (os .path .basename (file_path ),file_path )

        if self .plot_data_dict :
            self .current_file_path =next (iter (self .plot_data_dict ))
            self .update_settings_display (self .plot_data_dict [self .current_file_path ])

    def update_selected_plots (self ):
        if self .global_settings_chk .isChecked ():
            for file_path ,plot_data in self .plot_data_dict .items ():
                self .update_single_plot (file_path )
        elif self .current_file_path :
            self .update_single_plot (self .current_file_path )


    def update_single_plot (self ,file_path ):
        plot_data =self .plot_data_dict [file_path ]
        index =list (self .plot_data_dict .keys ()).index (file_path )
        plot_widget =self .plot_layout .itemAt (index ).widget ()
        canvas =plot_widget .layout ().itemAt (0 ).widget ()


        figure =canvas .figure 
        figure .clear ()


        ax =figure .add_subplot (111 )


        self .plot_data (ax ,plot_data )

        if plot_data .settings ['calculate_avg']and plot_data .settings ['avg_window_size']>0 :
            data_for_avg =plot_data .baseline_subtracted_data if plot_data .settings ['apply_baseline']else plot_data .data 
            rolling_avg =calculate_rolling_stats (data_for_avg ,plot_data .sampling_rate ,plot_data .settings ['avg_window_size'])
            ax .plot (plot_data .time ,rolling_avg ,linewidth =2 ,color ='red')

        if plot_data .settings ['use_segments']:
            self .plot_segments (ax ,plot_data )
        elif plot_data .settings ['use_threshold']:
            self .plot_threshold (ax ,plot_data )


        figure .tight_layout ()
        canvas .draw ()

        plot_data .original_settings =plot_data .settings .copy ()


    def update_settings_display (self ,plot_data ):
        settings =plot_data .settings 
        self .calculate_avg_chk .setChecked (settings ['calculate_avg'])
        self .avg_window_size_input .setText (str (settings ['avg_window_size']))
        self .threshold_chk .setChecked (settings ['use_threshold'])
        self .threshold_value_input .setValue (int (settings ['threshold_value']*1000 ))
        self .threshold_percentage_input .setValue (settings ['threshold_percentage'])
        self .select_segments_chk .setChecked (settings ['use_segments'])
        self .segment_list .clear ()
        for start ,end in settings ['segments']:
            self .segment_list .addItem (f"{start :.2f} - {end :.2f}")


    def update_avg_settings (self ):
        self .update_settings_from_ui ()

    def update_threshold_settings (self ):
        self .update_settings_from_ui ()

    def update_segment_settings (self ):
        self .update_settings_from_ui ()


    def plot_data (self ,ax ,plot_data ):
        nth_element =self .nth_element_spinbox .value ()
        if plot_data .settings ['apply_baseline']and plot_data .baseline_subtracted_data is not None :
            data_to_plot =plot_data .baseline_subtracted_data 
        else :
            data_to_plot =plot_data .data 

        line ,=ax .plot (plot_data .time [::nth_element ],data_to_plot [::nth_element ],linewidth =0.5 )
        ax .set_xlabel ('Time (s)')
        ax .set_ylabel ('Current (nA)')
        ax .set_xlim ([min (plot_data .time ),max (plot_data .time )])
        ax .set_title (os .path .basename (plot_data .file_path ))

        if plot_data .settings ['apply_baseline']:
            window_size =int ((plot_data .settings ['baseline_window_size']/1000 )*plot_data .sampling_rate )
            num_windows =len (plot_data .data )//window_size 
            for i in range (num_windows ):
                start =i *window_size 
                end =min ((i +1 )*window_size ,len (plot_data .time )-1 )



            if len (plot_data .data )%window_size !=0 :
                start =num_windows *window_size 


        return line 

    def add_plot_tab (self ,title ):
        tab =QWidget ()
        tab_layout =QVBoxLayout ()
        tab .setLayout (tab_layout )

        figure =Figure (figsize =(5 ,4 ),dpi =100 )
        canvas =FigureCanvasQTAgg (figure )
        tab_layout .addWidget (canvas )

        mpl_toolbar =NavigationToolbar2QT (canvas ,self )
        tab_layout .addWidget (mpl_toolbar )

        self .right_tab_widget .addTab (tab ,title )
        return figure ,canvas 


    def load_file (self ,file_path ):
        try :
            if file_path .endswith ('.abf'):
                raw_data ,sampling_rate ,time =load_abf_file (file_path )
            elif file_path .endswith ('.hdf5')or file_path .endswith ('.h5'):
                raw_data ,sampling_rate ,time =load_hdf5_file (file_path )
            elif file_path .endswith ('.dtlg'):
                raw_data ,sampling_rate ,time =load_dtlg_file (file_path )
            else :
                raise ValueError (f"Unsupported file format: {file_path }")

            unfiltered_data =raw_data .copy ()
            data =raw_data .copy ()

            if self .low_pass_filter_chk .isChecked ():
                filter_type =self .filter_type_dropdown .currentText ()
                cutoff_frequency =self .cutoff_frequency_spinbox .value ()*1000 

                if sampling_rate <=cutoff_frequency *2 :
                    raise ValueError (f"The selected cutoff frequency is too high for the sampling rate of {file_path }.")

                data =self .apply_low_pass_filter (data ,cutoff_frequency ,filter_type ,sampling_rate )

            return data ,unfiltered_data ,sampling_rate ,time 
        except Exception as e :
            raise Exception (f"Error loading {os .path .basename (file_path )}: {str (e )}")

    def clear_plot_layout (self ):
        while self .plot_layout .count ():
            item =self .plot_layout .takeAt (0 )
            widget =item .widget ()
            if widget :
                widget .deleteLater ()

        self .plot_layout .setSpacing (5 )
        self .plot_layout .setContentsMargins (5 ,5 ,5 ,5 )

    def find_contiguous_regions (self ,data ):
        contiguous_regions =[]
        data =np .sort (data )
        start_index =data [0 ]
        prev_index =start_index 
        for i in range (1 ,len (data )):
            if data [i ]>prev_index +1 :
                contiguous_regions .append ((start_index ,prev_index ))
                start_index =data [i ]
            prev_index =data [i ]
        contiguous_regions .append ((start_index ,data [-1 ]))
        return contiguous_regions 

    def plot_threshold (self ,ax ,plot_data ):
        settings =plot_data .settings 
        threshold_value =settings ['threshold_value']
        threshold_percentage =settings ['threshold_percentage']/100 
        avg_window_size_in_ms =settings ['avg_window_size']

        if avg_window_size_in_ms >0 :
            rolling_avg =calculate_rolling_stats (plot_data .data ,plot_data .sampling_rate ,avg_window_size_in_ms )
        else :
            rolling_avg =plot_data .data 

        threshold_lower =threshold_value -(threshold_value *(1 -threshold_percentage ))
        threshold_upper =threshold_value +(threshold_value *(1 -threshold_percentage ))

        selected_regions =np .where ((rolling_avg >=threshold_lower )&(rolling_avg <=threshold_upper ))[0 ]

        for region_start ,region_end in self .find_contiguous_regions (selected_regions ):
            start_time =plot_data .time [region_start ]
            end_time =plot_data .time [region_end ]
            ax .axvline (x =start_time ,color ='r',linestyle ='-',linewidth =0.5 )
            ax .axvline (x =end_time ,color ='r',linestyle ='-',linewidth =0.5 )
            ax .axvspan (start_time ,end_time ,alpha =0.3 ,color ='red')


    def plot_segments (self ,ax ,plot_data ):
        for start_time ,end_time in plot_data .settings ['segments']:
            ax .axvline (x =start_time ,color ='g',linestyle ='-',linewidth =0.5 )
            ax .axvline (x =end_time ,color ='g',linestyle ='-',linewidth =0.5 )
            ax .axvspan (start_time ,end_time ,alpha =0.3 ,color ='green')

    def toggle_select_segments (self ,state ):
        if state ==Qt .CheckState .Checked .value :
            self .segment_list .setEnabled (True )
            self .add_segment_btn .setEnabled (True )
            self .delete_segment_btn .setEnabled (True )
        else :
            self .segment_list .setEnabled (False )
            self .add_segment_btn .setEnabled (False )
            self .delete_segment_btn .setEnabled (False )
            self .segment_list .clear ()

        self .update_settings ()
        self .update_selected_plots ()

    def add_segment (self ):
        start_time ,ok =QInputDialog .getDouble (self ,"Add Segment","Start time (s):")
        if ok :
            end_time ,ok =QInputDialog .getDouble (self ,"Add Segment","End time (s):")
            if ok :
                self .segment_list .addItem (f"{start_time :.2f} - {end_time :.2f}")
                self .update_settings_from_ui ()

    def delete_segment (self ):
        current_row =self .segment_list .currentRow ()
        if current_row >=0 :
            self .segment_list .takeItem (current_row )
            self .update_settings_from_ui ()

    def get_segments_from_list (self ):
        segments =[]
        for i in range (self .segment_list .count ()):
            item =self .segment_list .item (i )
            start ,end =map (float ,item .text ().split (' - '))
            segments .append ((start ,end ))
        return segments 

    def save_selected_data (self ):
        if not self .plot_data_dict :
            QMessageBox .warning (self ,"Warning","No data to save.")
            return 
        directory =QFileDialog .getExistingDirectory (self ,"Select Directory to Save Files")
        if not directory :
            return 
        progress =QProgressDialog ("Saving files...","Cancel",0 ,len (self .plot_data_dict ),self )
        progress .setWindowModality (Qt .WindowModal )
        progress .setWindowTitle ("Please Wait")
        progress .setMinimumDuration (0 )

        saved_files =[]
        for i ,(file_path ,plot_data )in enumerate (self .plot_data_dict .items ()):
            if progress .wasCanceled ():
                break 
            try :
                result =self .save_plot_data (plot_data ,directory )
                if result :
                    saved_files .append (os .path .basename (result ))
                else :
                    QMessageBox .warning (self ,"Warning",f"No data selected for {os .path .basename (file_path )}. File not saved.")
            except Exception as e :
                QMessageBox .warning (self ,"Error",f"Failed to save data for {os .path .basename (file_path )}: {str (e )}")
            progress .setValue (i +1 )
            QApplication .processEvents ()
        progress .close ()

        if saved_files :
            message =f"Data saving process completed. {len (saved_files )} file(s) saved:\n"+"\n".join (saved_files )
            QMessageBox .information (self ,"Success",message )
        else :
            QMessageBox .warning (self ,"Warning","No files were saved.")

    def save_plot_data (self ,plot_data ,directory ):
        file_name =os .path .basename (plot_data .file_path )
        unfiltered_data =plot_data .unfiltered_data 
        sampling_rate =plot_data .sampling_rate 
        time =plot_data .time 
        settings =plot_data .settings 
        selected_indices =self .get_selected_indices (plot_data )

        if not np .any (selected_indices ):
            return False 

        selected_data =unfiltered_data [selected_indices ]
        selected_time =time [selected_indices ]

        base_name ,ext =os .path .splitext (file_name )
        output_filename =f"{base_name }_selected_unfiltered_data.h5"
        output_path =os .path .join (directory ,output_filename )

        with h5py .File (output_path ,'w')as f :
            f .create_dataset ('selected_data',data =selected_data )
            f .attrs ['sampling_rate']=sampling_rate 
            f .attrs ['original_file']=file_name 
            f .attrs ['duration']=selected_time [-1 ]-selected_time [0 ]

        with h5py .File (output_path ,'w')as f :
            f .create_dataset ('selected_data',data =selected_data )
            f .create_dataset ('selected_time',data =selected_time )
            if plot_data .settings ['apply_baseline']:
                selected_baseline_subtracted_data =plot_data .baseline_subtracted_unfiltered_data [selected_indices ]
                f .create_dataset ('selected_baseline_subtracted_data',data =selected_baseline_subtracted_data )
            f .attrs ['sampling_rate']=sampling_rate 
            f .attrs ['original_file']=file_name 
            f .attrs ['duration']=selected_time [-1 ]-selected_time [0 ]
            f .attrs ['apply_baseline']=plot_data .settings ['apply_baseline']
            if plot_data .settings ['apply_baseline']:
                f .attrs ['baseline_window_size']=plot_data .settings ['baseline_window_size']


        return output_path 

    def get_selected_indices (self ,plot_data ):
        settings =plot_data .settings 
        time =plot_data .time 
        if settings ['use_threshold']:

            rolling_avg =calculate_rolling_stats (plot_data .data ,plot_data .sampling_rate ,settings ['avg_window_size'])
            threshold_value =settings ['threshold_value']
            threshold_percentage =settings ['threshold_percentage']/100 
            threshold_lower =threshold_value -(threshold_value *(1 -threshold_percentage ))
            threshold_upper =threshold_value +(threshold_value *(1 -threshold_percentage ))
            return np .where ((rolling_avg >=threshold_lower )&(rolling_avg <=threshold_upper ))[0 ]
        elif settings ['use_segments']:
            indices =[]
            sorted_segments =sorted (settings ['segments'],key =lambda x :x [0 ])
            for start ,end in sorted_segments :
                start_idx =np .searchsorted (time ,start )
                end_idx =np .searchsorted (time ,end )
                indices .extend (range (start_idx ,end_idx +1 ))
            return np .array (indices )
        else :
            return np .arange (len (plot_data .data ))



if __name__ =='__main__':
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
    window =MainWindow ()
    window .showMaximized ()
    sys .exit (app .exec ())