import sys 
from PySide6 .QtWidgets import QApplication ,QMainWindow ,QWidget ,QHBoxLayout ,QVBoxLayout ,QPushButton ,QCheckBox ,QListWidget ,QLabel ,QFileDialog ,QLineEdit ,QMessageBox ,QListWidgetItem ,QSplitter ,QGroupBox ,QFormLayout ,QComboBox ,QSpinBox ,QTabWidget ,QDoubleSpinBox ,QGridLayout ,QStyleFactory ,QProgressBar 
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QIcon ,QFont ,QAction ,QPalette ,QColor 
import os 
import numpy as np 
from neo .rawio import AxonRawIO 
import matplotlib 
from matplotlib .backends .backend_qtagg import FigureCanvasQTAgg ,NavigationToolbar2QT 
from matplotlib .figure import Figure 
import h5py 
from scipy .signal import butter ,bessel ,cheby1 ,cheby2 ,ellip ,firwin ,lfilter ,sosfilt ,sosfilt_zi ,welch ,spectrogram 
import struct 

matplotlib .use ('Qt5Agg')

class MplCanvas (FigureCanvasQTAgg ):
    def __init__ (self ,parent =None ,width =5 ,height =4 ,dpi =100 ):
        fig =Figure (figsize =(width ,height ),dpi =dpi )
        self .axes =fig .add_subplot (111 )
        fig .tight_layout ()
        super ().__init__ (fig )

def load_abf_file (file_path ):
    """Load ABF file and return data, sampling rate, and time array."""
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
    """Load HDF5 file and return data, sampling rate, and time array."""
    with h5py .File (file_path ,'r')as f :
        selected_data =f ['selected_data'][()]
        sampling_rate =f .attrs ['sampling_rate']
        time =np .arange (len (selected_data ))/sampling_rate 
    return selected_data ,sampling_rate ,time 

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


class SegmentWidget (QWidget ):
    """Widget for adding segments."""
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        layout =QHBoxLayout ()
        self .setLayout (layout )

        self .start_label =QLabel ("Start (s):")
        self .start_input =QLineEdit ()
        self .end_label =QLabel ("End (s):")
        self .end_input =QLineEdit ()
        self .add_button =QPushButton ("Add Segment")

        layout .addWidget (self .start_label )
        layout .addWidget (self .start_input )
        layout .addWidget (self .end_label )
        layout .addWidget (self .end_input )
        layout .addWidget (self .add_button )

class SettingsWidget (QWidget ):
    """Widget for PSD and Spectrogram settings."""
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        layout =QGridLayout ()
        self .setLayout (layout )

        self .nperseg_psd_spinbox =QSpinBox ()
        self .nperseg_psd_spinbox .setRange (1 ,10000000 )
        self .nperseg_psd_spinbox .setValue (100000 )
        layout .addWidget (QLabel ("nperseg (PSD):"),0 ,0 )
        layout .addWidget (self .nperseg_psd_spinbox ,0 ,1 )

        self .noverlap_psd_spinbox =QSpinBox ()
        self .noverlap_psd_spinbox .setRange (0 ,10000000 )
        self .noverlap_psd_spinbox .setValue (128 )
        layout .addWidget (QLabel ("noverlap (PSD):"),0 ,2 )
        layout .addWidget (self .noverlap_psd_spinbox ,0 ,3 )

        self .scaling_psd_combobox =QComboBox ()
        self .scaling_psd_combobox .addItems (['density','spectrum'])
        layout .addWidget (QLabel ("scaling (PSD):"),1 ,0 )
        layout .addWidget (self .scaling_psd_combobox ,1 ,1 )

        self .nperseg_spectrogram_spinbox =QSpinBox ()
        self .nperseg_spectrogram_spinbox .setRange (1 ,1000000 )
        self .nperseg_spectrogram_spinbox .setValue (100000 )
        layout .addWidget (QLabel ("nperseg (Spectrogram):"),1 ,2 )
        layout .addWidget (self .nperseg_spectrogram_spinbox ,1 ,3 )

        self .return_onesided_spectrogram_checkbox =QCheckBox ()
        self .return_onesided_spectrogram_checkbox .setChecked (True )
        layout .addWidget (QLabel ("return_onesided (Spectrogram):"),2 ,0 )
        layout .addWidget (self .return_onesided_spectrogram_checkbox ,2 ,1 )

        self .plot_spectrogram_combobox =QComboBox ()
        self .plot_spectrogram_combobox .addItems (['pcolormesh','imshow'])
        layout .addWidget (QLabel ("Plot (Spectrogram):"),2 ,2 )
        layout .addWidget (self .plot_spectrogram_combobox ,2 ,3 )





class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD Spectrogram and PSD Plotter")
        self .setGeometry (100 ,100 ,1200 ,800 )

        self .data =None 
        self .sampling_rate =None 
        self .time =None 
        self .segments =[]

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

        nth_element_layout =QHBoxLayout ()


        self .app_name_label =QLabel ("SD Spectrogram and PSD Plotter")
        self .app_name_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .app_name_label .setStyleSheet ("font-size: 22px; font-weight: bold;")
        self .email_label =QLabel ("shankar.dutt@anu.edu.au")
        self .email_label .setAlignment (Qt .AlignmentFlag .AlignCenter )

        self .select_folder_btn =QPushButton ("Select Folder")
        self .select_folder_btn .clicked .connect (self .select_folder )

        self .include_subfolders_chk =QCheckBox ("Include Subfolders")

        self .files_list_widget =QListWidget ()
        self .files_list_widget .setSelectionMode (QListWidget .SelectionMode .ExtendedSelection )

        self .folder_path_label =QLabel (" ")
        self .folder_path_label .setWordWrap (True )

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

        self .plot_btn =QPushButton ("Plot Selected File")
        self .plot_btn .clicked .connect (self .plot_selected_file )

        left_layout .addWidget (self .app_name_label )
        left_layout .addWidget (self .email_label )
        left_layout .addWidget (self .select_folder_btn )
        left_layout .addWidget (self .include_subfolders_chk )
        left_layout .addWidget (self .files_list_widget )
        left_layout .addWidget (self .folder_path_label )
        left_layout .addLayout (nth_element_layout )
        left_layout .addWidget (self .low_pass_filter_chk )
        left_layout .addWidget (self .filter_type_label )
        left_layout .addWidget (self .filter_type_dropdown )
        left_layout .addWidget (self .cutoff_frequency_label )
        left_layout .addWidget (self .cutoff_frequency_spinbox )
        left_layout .addWidget (self .plot_btn )


        self .tab_widget =QTabWidget ()
        right_layout .addWidget (self .tab_widget )

        self .plots_tab =QWidget ()
        self .plots_tab_layout =QVBoxLayout ()
        self .plots_tab .setLayout (self .plots_tab_layout )
        self .tab_widget .addTab (self .plots_tab ,"Plots")

        self .psd_tab =QWidget ()
        self .psd_canvas =MplCanvas (self ,width =8 ,height =6 ,dpi =100 )
        self .psd_toolbar =NavigationToolbar2QT (self .psd_canvas ,self )
        psd_layout =QVBoxLayout ()
        psd_layout .addWidget (self .psd_canvas )
        psd_layout .addWidget (self .psd_toolbar )
        self .psd_tab .setLayout (psd_layout )
        self .tab_widget .addTab (self .psd_tab ,"PSD")

        self .spectrogram_tab =QWidget ()
        self .spectrogram_tab_layout =QVBoxLayout ()
        self .spectrogram_tab .setLayout (self .spectrogram_tab_layout )
        self .tab_widget .addTab (self .spectrogram_tab ,"Spectrogram")

        bottom_layout =QHBoxLayout ()
        self .plot_spectrogram_btn =QPushButton ("Plot Spectrogram")
        self .plot_spectrogram_btn .clicked .connect (self .plot_spectrogram )
        self .plot_psd_btn =QPushButton ("Plot PSD")
        self .plot_psd_btn .clicked .connect (self .plot_psd )
        bottom_layout .addWidget (self .plot_spectrogram_btn )
        bottom_layout .addWidget (self .plot_psd_btn )
        right_layout .addLayout (bottom_layout )

        self .settings_group =QGroupBox ("Settings")
        self .settings_layout =QVBoxLayout ()
        self .settings_group .setLayout (self .settings_layout )
        self .settings_widget =SettingsWidget ()
        self .settings_layout .addWidget (self .settings_widget )
        right_layout .addWidget (self .settings_group )

        self .plot_tabs ={}
        self .spectrogram_tabs ={}
        self .plots_tab_widget =QTabWidget ()
        self .plots_tab_layout .addWidget (self .plots_tab_widget )

        self .spectrogram_tab_widget =QTabWidget ()
        self .spectrogram_tab_layout .addWidget (self .spectrogram_tab_widget )


        self .progress_bar =QProgressBar ()
        self .progress_bar .setVisible (False )
        left_layout .addWidget (self .progress_bar )

    def toggle_low_pass_filter (self ,state ):
        """Enable or disable filter settings based on checkbox state."""
        self .filter_type_dropdown .setEnabled (state ==Qt .CheckState .Checked .value )
        self .cutoff_frequency_spinbox .setEnabled (state ==Qt .CheckState .Checked .value )

    def select_folder (self ):
        """Handle folder selection and populate the file list."""
        options =QFileDialog .Option .ShowDirsOnly 
        directory =QFileDialog .getExistingDirectory (self ,"Select Folder","",options =options )
        if directory :
            self .folder_path_label .setText (f"Selected folder: {directory }")
            self .populate_file_list (directory ,self .include_subfolders_chk .isChecked ())

    def apply_low_pass_filter (self ,data ,cutoff_frequency ,filter_type ,sampling_rate ):
        """Apply the selected low pass filter to the data."""
        nyquist_rate =sampling_rate /2.0 
        cutoff =cutoff_frequency /nyquist_rate 
        sos =None 
        if filter_type =='Butterworth':
            sos =butter (N =8 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
        elif filter_type =='Bessel':
            sos =bessel (N =8 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
        elif filter_type =='Chebyshev I':
            sos =cheby1 (N =8 ,rp =0.1 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
        elif filter_type =='Chebyshev II':
            sos =cheby2 (N =8 ,rs =40 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
        elif filter_type =='Elliptic':
            sos =ellip (N =8 ,rp =0.1 ,rs =40 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
        elif filter_type =='FIR':
            taps =firwin (101 ,cutoff )
            return lfilter (taps ,1 ,data )
        elif filter_type =='IIR':
            b ,a =butter (N =8 ,Wn =cutoff ,btype ='low',analog =False )
            return lfilter (b ,a ,data )

        if sos is not None :
            zi =sosfilt_zi (sos )*data [0 ]
            return sosfilt (sos ,data ,zi =zi )[0 ]
        return data 















    def populate_file_list (self ,directory ,include_subfolders ):
        """Populate the file list with ABF and HDF5 files, sorted by name."""
        self .files_list_widget .clear ()
        file_list =[]

        for root ,dirs ,files in os .walk (directory ):
            for file in files :
                if file .endswith (('.abf','.hdf5','.h5','.dtlg')):
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

    def plot_selected_file (self ):
        """Plot the selected files."""
        selected_items =self .files_list_widget .selectedItems ()
        if not selected_items :
            QMessageBox .warning (self ,"Error","No file selected.")
            return 

        self .data_dict ={}
        self .sampling_rate_dict ={}
        self .time_dict ={}

        self .progress_bar .setVisible (True )
        self .progress_bar .setRange (0 ,len (selected_items ))
        self .progress_bar .setValue (0 )

        for i ,item in enumerate (selected_items ):
            file_path =item .data (Qt .ItemDataRole .UserRole )
            try :
                if file_path .endswith ('.abf'):
                    data ,sampling_rate ,time =load_abf_file (file_path )
                elif file_path .endswith (('.hdf5','.h5')):
                    data ,sampling_rate ,time =load_hdf5_file (file_path )
                elif file_path .endswith ('.dtlg'):
                    data ,sampling_rate ,time =load_dtlg_file (file_path )
                else :
                    raise ValueError (f"Unsupported file format: {file_path }")

                if self .low_pass_filter_chk .isChecked ():
                    filter_type =self .filter_type_dropdown .currentText ()
                    cutoff_frequency =self .cutoff_frequency_spinbox .value ()*1000 

                    if sampling_rate <=cutoff_frequency *2 :
                        QMessageBox .warning (self ,"Error",f"The selected cutoff frequency ({cutoff_frequency } Hz) is too high for the sampling rate ({sampling_rate } Hz).")
                        continue 

                    data =self .apply_low_pass_filter (data ,cutoff_frequency ,filter_type ,sampling_rate )

                self .data_dict [file_path ]=data 
                self .sampling_rate_dict [file_path ]=sampling_rate 
                self .time_dict [file_path ]=time 

                if file_path not in self .plot_tabs :
                    plot_tab =self .create_plot_tab (file_path )
                    self .plot_tabs [file_path ]=plot_tab 

                self .update_plot (file_path )
                self .progress_bar .setValue (i +1 )
                QApplication .processEvents ()

            except Exception as e :
                QMessageBox .warning (self ,"Error",f"Failed to load or process {file_path }: {str (e )}")
        self .progress_bar .setVisible (False )

    def create_plot_tab (self ,file_path ):
        """Create a new tab for the selected file."""
        plot_tab =QWidget ()
        plot_layout =QVBoxLayout ()
        plot_tab .setLayout (plot_layout )

        canvas =MplCanvas (self ,width =8 ,height =6 ,dpi =100 )
        mpl_toolbar =NavigationToolbar2QT (canvas ,self )

        canvas_layout =QVBoxLayout ()
        canvas_layout .addWidget (canvas )
        canvas_layout .addWidget (mpl_toolbar )

        select_segments_group =QGroupBox ("Select Segments")
        select_segments_layout =QGridLayout ()
        select_segments_group .setLayout (select_segments_layout )

        segment_widget =SegmentWidget ()
        segment_widget .add_button .clicked .connect (lambda _ ,f =file_path :self .add_segment (f ))
        select_segments_layout .addWidget (segment_widget ,0 ,0 ,1 ,2 )

        segment_dropdown =QComboBox ()
        segment_dropdown .setEnabled (False )
        select_segments_layout .addWidget (segment_dropdown ,1 ,0 )

        delete_segment_btn =QPushButton ("Delete Segment")
        delete_segment_btn .setEnabled (False )
        delete_segment_btn .clicked .connect (lambda _ ,f =file_path :self .delete_segment (f ))
        select_segments_layout .addWidget (delete_segment_btn ,1 ,1 )

        plot_layout .addLayout (canvas_layout )
        plot_layout .addWidget (select_segments_group )

        file_name =os .path .basename (file_path )
        self .plots_tab_widget .addTab (plot_tab ,file_name )

        return {
        'tab':plot_tab ,
        'canvas':canvas ,
        'segment_widget':segment_widget ,
        'segment_dropdown':segment_dropdown ,
        'delete_segment_btn':delete_segment_btn ,
        'segments':[]
        }

    def add_segment (self ,file_path ):
        """Add a segment to the plot."""
        try :
            start_time =float (self .plot_tabs [file_path ]['segment_widget'].start_input .text ())
            end_time =float (self .plot_tabs [file_path ]['segment_widget'].end_input .text ())
            if start_time >=end_time :
                raise ValueError ("Start time must be less than end time.")
            if start_time <0 or end_time >max (self .time_dict [file_path ]):
                raise ValueError ("Segment times are out of range.")
            self .plot_tabs [file_path ]['segments'].append ((start_time ,end_time ))
            segment_label =f"Segment: {start_time :.2f} - {end_time :.2f}"
            self .plot_tabs [file_path ]['segment_dropdown'].addItem (segment_label )
            self .plot_tabs [file_path ]['segment_dropdown'].setEnabled (True )
            self .plot_tabs [file_path ]['delete_segment_btn'].setEnabled (True )
            self .update_plot (file_path )
        except ValueError as e :
            QMessageBox .warning (self ,"Error",str (e ))

    def delete_segment (self ,file_path ):
        """Delete a segment from the plot."""
        if self .plot_tabs [file_path ]['segment_dropdown'].count ()>0 :
            index =self .plot_tabs [file_path ]['segment_dropdown'].currentIndex ()
            self .plot_tabs [file_path ]['segments'].pop (index )
            self .plot_tabs [file_path ]['segment_dropdown'].removeItem (index )
            if self .plot_tabs [file_path ]['segment_dropdown'].count ()==0 :
                self .plot_tabs [file_path ]['segment_dropdown'].setEnabled (False )
                self .plot_tabs [file_path ]['delete_segment_btn'].setEnabled (False )
            self .update_plot (file_path )

    def update_plot (self ,file_path ):
        """Update the plot with data and segments."""
        data =self .data_dict [file_path ]
        time =self .time_dict [file_path ]

        canvas =self .plot_tabs [file_path ]['canvas']
        canvas .axes .clear ()
        nth_element =self .nth_element_spinbox .value ()
        canvas .axes .plot (time [::nth_element ],data [::nth_element ],linewidth =0.5 )
        canvas .axes .set_xlabel ('Time (s)')
        canvas .axes .set_ylabel ('Current (nA)')
        canvas .axes .set_xlim ([min (time ),max (time )])

        for start_time ,end_time in self .plot_tabs [file_path ]['segments']:
            canvas .axes .axvline (x =start_time ,color ='g',linestyle ='-',linewidth =0.5 )
            canvas .axes .axvline (x =end_time ,color ='g',linestyle ='-',linewidth =0.5 )
            canvas .axes .axvspan (start_time ,end_time ,alpha =0.3 ,color ='green')

        canvas .draw ()

    def plot_spectrogram (self ):
        """Plot spectrogram for the selected segments."""
        if not self .data_dict :
            QMessageBox .warning (self ,"Error","No data loaded.")
            return 


        self .progress_bar .setVisible (True )
        self .progress_bar .setRange (0 ,len (self .data_dict ))
        self .progress_bar .setValue (0 )

        for i ,(file_path ,data )in enumerate (self .data_dict .items ()):
            sampling_rate =self .sampling_rate_dict [file_path ]
            time =self .time_dict [file_path ]

            if file_path not in self .spectrogram_tabs :
                spectrogram_tab =QWidget ()
                spectrogram_layout =QVBoxLayout ()
                spectrogram_tab .setLayout (spectrogram_layout )

                spectrogram_canvas =MplCanvas (self ,width =8 ,height =6 ,dpi =100 )
                spectrogram_toolbar =NavigationToolbar2QT (spectrogram_canvas ,self )
                spectrogram_layout .addWidget (spectrogram_canvas )
                spectrogram_layout .addWidget (spectrogram_toolbar )

                self .spectrogram_tabs [file_path ]={
                'tab':spectrogram_tab ,
                'canvas':spectrogram_canvas ,
                'colorbar':None 
                }

                file_name =os .path .basename (file_path )
                self .spectrogram_tab_widget .addTab (spectrogram_tab ,file_name )

            spectrogram_canvas =self .spectrogram_tabs [file_path ]['canvas']
            spectrogram_canvas .axes .clear ()

            segments =self .plot_tabs [file_path ]['segments']
            if not segments :
                QMessageBox .warning (self ,"Error",f"No segments defined for {file_path }")
                continue 

            for start_time ,end_time in segments :
                start_index =np .searchsorted (time ,start_time )
                end_index =np .searchsorted (time ,end_time )
                segment_data =data [start_index :end_index ]
                segment_time =time [start_index :end_index ]-time [start_index ]

                nperseg =min (self .settings_widget .nperseg_spectrogram_spinbox .value (),len (segment_data ))
                return_onesided =self .settings_widget .return_onesided_spectrogram_checkbox .isChecked ()
                plot_type =self .settings_widget .plot_spectrogram_combobox .currentText ()

                freq ,time_spec ,Sxx =spectrogram (segment_data ,fs =sampling_rate ,nperseg =nperseg ,return_onesided =return_onesided )
                Sxx_db =10 *np .log10 (Sxx )

                if plot_type =='pcolormesh':
                    im =spectrogram_canvas .axes .pcolormesh (time_spec +segment_time [0 ],freq ,Sxx_db ,shading ='gouraud',cmap ='viridis')
                elif plot_type =='imshow':
                    extent =[segment_time [0 ],segment_time [-1 ],freq [0 ],freq [-1 ]]
                    im =spectrogram_canvas .axes .imshow (Sxx_db ,extent =extent ,aspect ='auto',cmap ='viridis',origin ='lower')

                spectrogram_canvas .axes .set_xlabel ('Time (s)')
                spectrogram_canvas .axes .set_ylabel ('Frequency (Hz)')
                spectrogram_canvas .axes .set_title (f'Spectrogram - Segment: {start_time :.2f}s to {end_time :.2f}s')

                if self .spectrogram_tabs [file_path ]['colorbar']is None :
                    self .spectrogram_tabs [file_path ]['colorbar']=spectrogram_canvas .figure .colorbar (im ,ax =spectrogram_canvas .axes )
                else :
                    self .spectrogram_tabs [file_path ]['colorbar'].update_normal (im )

                self .spectrogram_tabs [file_path ]['colorbar'].set_label ('Magnitude (dB)')







                self .progress_bar .setValue (i +1 )
                QApplication .processEvents ()


            spectrogram_canvas .figure .tight_layout ()
            spectrogram_canvas .draw ()

        self .progress_bar .setVisible (False )
        self .tab_widget .setCurrentWidget (self .spectrogram_tab )

    def plot_psd (self ):
        """Plot PSD for the selected segments."""
        if not self .data_dict :
            QMessageBox .warning (self ,"Error","No data loaded.")
            return 

        self .psd_canvas .axes .clear ()
        self .progress_bar .setVisible (True )
        self .progress_bar .setRange (0 ,len (self .data_dict ))
        self .progress_bar .setValue (0 )

        scaling =self .settings_widget .scaling_psd_combobox .currentText ()

        for i ,(file_path ,data )in enumerate (self .data_dict .items ()):
            sampling_rate =self .sampling_rate_dict [file_path ]
            segments =self .plot_tabs [file_path ]['segments']

            if not segments :
                QMessageBox .warning (self ,"Error",f"No segments defined for {file_path }")
                continue 

            for start_time ,end_time in segments :
                start_index =np .searchsorted (self .time_dict [file_path ],start_time )
                end_index =np .searchsorted (self .time_dict [file_path ],end_time )
                segment_data =data [start_index :end_index ]

                freq ,psd_values =self .calculate_psd (segment_data ,sampling_rate )
                label =f"{os .path .basename (file_path )} - [{start_time :.2f}, {end_time :.2f}]"
                self .psd_canvas .axes .loglog (freq ,psd_values ,linewidth =0.5 ,label =label )
            self .progress_bar .setValue (i +1 )
            QApplication .processEvents ()

        self .psd_canvas .axes .set_xlabel ('Frequency (Hz)')

        if scaling =='density':
            self .psd_canvas .axes .set_ylabel ('PSD (nA²/Hz)')
        elif scaling =='spectrum':
            self .psd_canvas .axes .set_ylabel ('Power Spectrum (nA²)')

        self .psd_canvas .axes .set_xlim ([0.1 ,max (self .sampling_rate_dict .values ())/2 ])
        self .psd_canvas .axes .legend ()
        self .psd_canvas .figure .tight_layout ()
        self .psd_canvas .draw ()
        self .progress_bar .setVisible (False )
        self .tab_widget .setCurrentWidget (self .psd_tab )

    def calculate_psd (self ,data ,sampling_rate ):
        """Calculate the Power Spectral Density (PSD) of the given data, adjusted for nA units."""
        nperseg =min (self .settings_widget .nperseg_psd_spinbox .value (),len (data ))
        noverlap =min (self .settings_widget .noverlap_psd_spinbox .value (),nperseg -1 )
        scaling =self .settings_widget .scaling_psd_combobox .currentText ()

        freq ,psd =welch (data ,fs =sampling_rate ,nperseg =nperseg ,noverlap =noverlap ,scaling =scaling )

        if scaling =='density':
            psd_values =psd 
        elif scaling =='spectrum':
            df =freq [1 ]-freq [0 ]
            psd_values =psd *df 

        return freq ,psd_values 

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

    try :
        window =MainWindow ()
        window .showMaximized ()
        sys .exit (app .exec ())
    except Exception as e :
        QMessageBox .critical (None ,"Error",f"An unexpected error occurred: {str (e )}")
        sys .exit (1 )