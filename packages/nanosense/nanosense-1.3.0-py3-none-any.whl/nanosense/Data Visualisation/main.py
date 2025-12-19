import sys 
import os 
import json 
from typing import List 
import numpy as np 
import pandas as pd 
from tabulate import tabulate 
from PySide6 .QtWidgets import (
QApplication ,QMainWindow ,QWidget ,QDialog ,
QVBoxLayout ,QHBoxLayout ,QGridLayout ,QFormLayout ,
QLabel ,QPushButton ,QRadioButton ,QCheckBox ,
QTabWidget ,QGroupBox ,QSpinBox ,QSlider ,QComboBox ,
QTableWidget ,QTableWidgetItem ,QHeaderView ,
QFileDialog ,QMessageBox ,QSplitter ,QScrollArea ,
QButtonGroup ,QStyleFactory ,QMenuBar ,QLineEdit ,QListWidget ,QAbstractItemView ,QTextEdit 
)
from PySide6 .QtGui import QIcon ,QFont ,QAction ,QPalette ,QColor 
from PySide6 .QtCore import Qt ,QTimer 
import matplotlib .pyplot as plt 
import matplotlib .gridspec as gridspec 
import matplotlib .cm as cm 
from matplotlib .figure import Figure 
from matplotlib .backends .backend_qtagg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib .backends .backend_qtagg import NavigationToolbar2QT as NavigationToolbar 
from matplotlib .colors import LogNorm ,PowerNorm ,Normalize 
from sklearn .decomposition import PCA 
from sklearn .preprocessing import StandardScaler 
from matplotlib .ticker import NullFormatter 
import scipy 
from scipy import stats 
from scipy .stats import (
norm ,lognorm ,poisson ,weibull_min ,
gaussian_kde )
from sklearn .cluster import KMeans 
from scipy .special import erf ,factorial ,gammaln ,erfc 
from scipy .signal import find_peaks 
from scipy .optimize import curve_fit 
from sklearn .mixture import GaussianMixture 
from sklearn .decomposition import PCA ,KernelPCA ,IncrementalPCA 
import seaborn as sns 
from lmfit import Model ,CompositeModel ,Parameters 
from lmfit .models import (GaussianModel ,LorentzianModel ,VoigtModel ,PseudoVoigtModel ,
MoffatModel ,Pearson4Model ,Pearson7Model ,StudentsTModel ,
BreitWignerModel ,LognormalModel ,ExponentialGaussianModel ,
SkewedGaussianModel ,SkewedVoigtModel ,ThermalDistributionModel ,
LinearModel ,QuadraticModel ,PolynomialModel ,ExponentialModel ,
PowerLawModel )
import re 
import traceback 
from sklearn .preprocessing import StandardScaler ,normalize ,Normalizer 
from sklearn .cluster import KMeans 
import warnings 
from factor_analyzer .factor_analyzer import calculate_kmo 

MAX_FILES =11 

colorlist =['orange','red','green','blue','lime','navy','teal','olive','maroon','darkcyan','silver','gray']

cmaps =plt .colormaps ()

def safe_log (x ):
    return np .log (np .clip (x ,1e-10 ,None ))


def students_t_model (x ,amplitude ,center ,sigma ,df ):
    return amplitude *(1 +((x -center )/sigma )**2 /df )**(-0.5 *(df +1 ))

def setup_students_t (prefix ='m',n_components =1 ):
    model =None 
    params =Parameters ()
    for i in range (n_components ):
        m =Model (students_t_model ,prefix =f'{prefix }{i }_')
        if model is None :
            model =m 
        else :
            model +=m 
        params .update (m .make_params ())
        params [f'{prefix }{i }_amplitude'].set (value =1 ,min =0 )
        params [f'{prefix }{i }_center'].set (value =0 )
        params [f'{prefix }{i }_sigma'].set (value =1 ,min =0 )
        params [f'{prefix }{i }_df'].set (value =2 ,min =1 )
    return model ,params 


def exp_gaussian (x ,center ,sigma ,gamma ):
    """
    Return an exponential Gaussian function.
    """
    arg =(x -center )/(sigma *np .sqrt (2 ))
    return (gamma /2 )*np .exp (gamma *(gamma *sigma *sigma /2 +center -x ))*erfc (arg -gamma *sigma /np .sqrt (2 ))

def exp_gaussian_model (x ,amplitude ,center ,sigma ,gamma ):
    return amplitude *exp_gaussian (x ,center ,sigma ,gamma )

def setup_exp_gaussian (prefix ='m',n_components =1 ):
    model =None 
    params =Parameters ()
    for i in range (n_components ):
        m =Model (exp_gaussian_model ,prefix =f'{prefix }{i }_')
        if model is None :
            model =m 
        else :
            model +=m 
        params .update (m .make_params ())
        params [f'{prefix }{i }_amplitude'].set (value =1 ,min =0 )
        params [f'{prefix }{i }_center'].set (value =0 )
        params [f'{prefix }{i }_sigma'].set (value =1 ,min =0 )
        params [f'{prefix }{i }_gamma'].set (value =1 ,min =0 )
    return model ,params 

def setup_skewed_voigt (prefix ='m',n_components =1 ):
    model =None 
    params =Parameters ()
    for i in range (n_components ):
        m =SkewedVoigtModel (prefix =f'{prefix }{i }_')
        if model is None :
            model =m 
        else :
            model +=m 
        params .update (m .make_params ())
        params [f'{prefix }{i }_amplitude'].set (value =1 ,min =0 )
        params [f'{prefix }{i }_center'].set (value =0 )
        params [f'{prefix }{i }_sigma'].set (value =1 ,min =0 )
        params [f'{prefix }{i }_gamma'].set (value =1 ,min =0 )
        params [f'{prefix }{i }_skew'].set (value =0 )
    return model ,params 

def setup_linear (prefix ='m',n_components =1 ):
    model =None 
    params =Parameters ()
    for i in range (n_components ):
        m =LinearModel (prefix =f'{prefix }{i }_')
        if model is None :
            model =m 
        else :
            model +=m 
        params .update (m .make_params ())
        params [f'{prefix }{i }_slope'].set (value =1 )
        params [f'{prefix }{i }_intercept'].set (value =0 )
    return model ,params 


def remove_nan_arrays (X ):

    X_filtered =X [~np .isnan (X ).any (axis =1 )]


    num_removed =X .shape [0 ]-X_filtered .shape [0 ]

    return X_filtered ,num_removed 


def interpret_kmo (kmo_value ):
        if kmo_value >=0.9 :
            return "Marvelous"
        elif kmo_value >=0.8 :
            return "Meritorious"
        elif kmo_value >=0.7 :
            return "Middling"
        elif kmo_value >=0.6 :
            return "Mediocre"
        elif kmo_value >=0.5 :
            return "Miserable"
        else :
            return "Unacceptable"

class NewDataDialog (QDialog ):
    def __init__ (self ,parent =None ,n_features =None ):
        super ().__init__ (parent )
        self .n_features =n_features 
        self .setWindowTitle ("Enter New Data")
        layout =QVBoxLayout (self )

        self .inputs =[]
        for i in range (n_features ):
            label =QLabel (f"Feature {i +1 }:")
            input_field =QLineEdit ()
            layout .addWidget (label )
            layout .addWidget (input_field )
            self .inputs .append (input_field )

        submit_button =QPushButton ("Submit")
        submit_button .clicked .connect (self .accept )
        layout .addWidget (submit_button )

    def get_data (self ):
        return [float (input_field .text ())for input_field in self .inputs ]


class PCAAnalyzer :
    def __init__ (self ):
        self .pca =None 
        self .scaler =None 
        self .data =None 
        self .transformed_data =None 

    def preprocess_data (self ,data ,method ='standardize'):
        if method =='standardize':
            self .scaler =StandardScaler ()
        else :
            self .scaler =Normalizer ()
        return self .scaler .fit_transform (data )

    def perform_pca (self ,data ,n_components ,pca_type ='standard',kernel ='rbf',preprocess_method ='standardize'):
        self .data =data 
        preprocessed_data =self .preprocess_data (data ,method =preprocess_method )

        if pca_type =='standard':
            self .pca =PCA (n_components =n_components )
        elif pca_type =='kernel':
            self .pca =KernelPCA (n_components =n_components ,kernel =kernel )
        else :
            self .pca =IncrementalPCA (n_components =n_components )

        self .transformed_data =self .pca .fit_transform (preprocessed_data )
        return self .transformed_data 

    @staticmethod 
    def calculate_kmo_test (self ,data ):
        with warnings .catch_warnings (record =True )as w :
            warnings .simplefilter ("always")
            try :
                kmo_all ,kmo_model =calculate_kmo (data )
                if len (w )>0 and issubclass (w [-1 ].category ,UserWarning ):
                    print ("Warning: KMO test used Moore-Penrose inverse. Results may be less reliable.")
                return kmo_model 
            except Exception as e :
                print (f"KMO calculation failed: {str (e )}")
                return None 

    def get_explained_variance_ratio (self ):
        if hasattr (self .pca ,'explained_variance_ratio_'):
            return self .pca .explained_variance_ratio_ 
        else :
            return None 

    def get_feature_contributions (self ):
        if hasattr (self .pca ,'components_'):
            return self .pca .components_ 
        else :
            return None 

    def perform_clustering (self ,n_clusters ):
        kmeans =KMeans (n_clusters =n_clusters )
        return kmeans .fit_predict (self .transformed_data )

    def project_new_data (self ,new_data ):
        preprocessed_data =self .scaler .transform (new_data )
        return self .pca .transform (preprocessed_data )




class LoadDataTab (QWidget ):
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        self .parent =parent 
        self .layout =QVBoxLayout (self )

        self .select_folder_button =QPushButton ("Select Folder")
        self .select_folder_button .clicked .connect (self .select_folder )

        self .include_subfolders_checkbox =QCheckBox ("Include Subfolders")
        self .include_subfolders_checkbox .stateChanged .connect (self .populate_file_list )

        self .file_list =QListWidget ()
        self .file_list .setSelectionMode (QAbstractItemView .SingleSelection )

        self .selected_folder_label =QLabel ("No folder selected")
        self .selected_folder_label .setWordWrap (True )

        self .layout .addWidget (self .select_folder_button )
        self .layout .addWidget (self .include_subfolders_checkbox )
        self .layout .addWidget (self .file_list )
        self .layout .addWidget (self .selected_folder_label )


    def select_folder (self ):
        folder =QFileDialog .getExistingDirectory (self ,"Select Folder")
        if folder :
            self .parent .folder_path =folder 
            self .selected_folder_label .setText (f"Selected folder: {folder }")
            self .populate_file_list ()

    def populate_file_list (self ):
        if not self .parent .folder_path :
            return 
        self .file_list .clear ()
        if self .include_subfolders_checkbox .isChecked ():
            for root ,dirs ,files in os .walk (self .parent .folder_path ):
                for file in files :
                    if file .endswith ('.dataset.npz'):
                        relative_path =os .path .relpath (os .path .join (root ,file ),self .parent .folder_path )
                        self .file_list .addItem (relative_path )
        else :
            for file in os .listdir (self .parent .folder_path ):
                if file .endswith ('.dataset.npz'):
                    self .file_list .addItem (file )
        self .file_list .sortItems ()


class FitParameterWindow (QMainWindow ):
    def __init__ (self ,parent =None ,fit_params =None ,fit_type =None ):
        super ().__init__ (parent )
        self .setWindowTitle ("Fit Parameters")
        self .setGeometry (100 ,100 ,400 ,300 )

        central_widget =QWidget ()
        self .setCentralWidget (central_widget )
        layout =QVBoxLayout (central_widget )

        self .param_widgets ={}
        for param_name ,param in fit_params .items ():
            param_layout =QHBoxLayout ()
            param_layout .addWidget (QLabel (param_name ))


            if hasattr (param ,'value'):
                param_value =param .value 
            else :
                param_value =param 

            param_edit =QLineEdit (f"{param_value :.6g}")
            self .param_widgets [param_name ]=param_edit 
            param_layout .addWidget (param_edit )
            layout .addLayout (param_layout )

        self .update_button =QPushButton ("Update Plot")
        self .update_button .clicked .connect (self .update_plot )
        layout .addWidget (self .update_button )

        self .send_to_fitting_button =QPushButton ("Send to Fitting")
        self .send_to_fitting_button .clicked .connect (self .send_to_fitting )
        layout .addWidget (self .send_to_fitting_button )

        self .parent_app =parent 

    def get_params (self ):
        return {param :float (widget .text ())for param ,widget in self .param_widgets .items ()}

    def update_plot (self ):
        new_params =self .get_params ()
        self .parent_app .update_plot_with_params (new_params ,refit =False )

    def update_params (self ,new_params ):
        for param_name ,param in new_params .items ():
            if param_name in self .param_widgets :

                if hasattr (param ,'value'):
                    param_value =param .value 
                else :
                    param_value =param 
                self .param_widgets [param_name ].setText (f"{param_value :.6g}")

    def send_to_fitting (self ):
        new_params =self .get_params ()
        self .parent_app .send_to_fitting (new_params )

class FitResultsTab (QWidget ):
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        self .layout =QVBoxLayout (self )


        self .table =QTableWidget ()
        self .layout .addWidget (QLabel ("Regular Fit Results:"))
        self .layout .addWidget (self .table )

        self .gof_layout =QHBoxLayout ()
        self .r_squared_label =QLabel ("R²: ")
        self .chi_square_label =QLabel ("Chi-square: ")
        self .reduced_chi_square_label =QLabel ("Reduced Chi-square: ")
        self .gof_layout .addWidget (self .r_squared_label )
        self .gof_layout .addWidget (self .chi_square_label )
        self .gof_layout .addWidget (self .reduced_chi_square_label )
        self .layout .addLayout (self .gof_layout )


        self .time_series_fit_results_table =QTableWidget ()
        self .layout .addWidget (QLabel ("Time Series Fit Results:"))
        self .layout .addWidget (self .time_series_fit_results_table )

    def update_results (self ,fit_results ,r_squared ,chi_square ,reduced_chi_square ):
        self .table .clear ()
        self .table .setRowCount (0 )
        self .table .setColumnCount (3 )
        self .table .setHorizontalHeaderLabels (["Component","Parameter","Value ± Uncertainty"])

        row =0 
        for component ,params in fit_results .items ():
            for param_name ,param_data in params .items ():
                self .table .insertRow (row )
                self .table .setItem (row ,0 ,QTableWidgetItem (component ))
                self .table .setItem (row ,1 ,QTableWidgetItem (param_name ))
                value =f"{param_data ['value']:.6f}"
                if param_data ['uncertainty']!='N/A':
                    value +=f" ± {param_data ['uncertainty']:.6f}"
                self .table .setItem (row ,2 ,QTableWidgetItem (value ))
                row +=1 

        self .table .resizeColumnsToContents ()
        self .r_squared_label .setText (f"R²: {r_squared :.4f}")
        self .chi_square_label .setText (f"Chi-square: {chi_square :.4f}")
        self .reduced_chi_square_label .setText (f"Reduced Chi-square: {reduced_chi_square :.4f}")

    def update_time_series_fit_results (self ,fit_results ,times ):
        self .time_series_fit_results_table .clear ()
        self .time_series_fit_results_table .setRowCount (0 )

        headers =['Time (min)','Component','Amplitude','Center','Sigma','R-squared','Chi-square']
        self .time_series_fit_results_table .setColumnCount (len (headers ))
        self .time_series_fit_results_table .setHorizontalHeaderLabels (headers )

        row =0 
        for time ,fit_result in zip (times ,fit_results ):
            if fit_result is None or 'result'not in fit_result or fit_result ['result']is None :
                continue 

            result =fit_result ['result']
            r_squared =1 -(result .residual .var ()/np .var (result .data ))
            chi_square =np .sum (result .residual **2 )

            for i ,prefix in enumerate (set (name .split ('_')[0 ]for name in result .params )):
                self .time_series_fit_results_table .insertRow (row )

                self .time_series_fit_results_table .setItem (row ,0 ,QTableWidgetItem (f"{time :.2f}"))
                self .time_series_fit_results_table .setItem (row ,1 ,QTableWidgetItem (f"Component {i +1 }"))

                amplitude =result .params [f'{prefix }_amplitude']
                center =result .params [f'{prefix }_center']
                sigma =result .params [f'{prefix }_sigma']

                for col ,param in enumerate ([amplitude ,center ,sigma ],start =2 ):
                    item =QTableWidgetItem (f"{param .value :.4f}")
                    item .setToolTip (f"Value: {param .value :.6f}\nStd Error: {param .stderr :.6f}"if param .stderr else "Std Error: N/A")
                    self .time_series_fit_results_table .setItem (row ,col ,item )


                if i ==0 :
                    self .time_series_fit_results_table .setItem (row ,5 ,QTableWidgetItem (f"{r_squared :.4f}"))
                    self .time_series_fit_results_table .setItem (row ,6 ,QTableWidgetItem (f"{chi_square :.4f}"))

                row +=1 

        self .time_series_fit_results_table .resizeColumnsToContents ()
        self .time_series_fit_results_table .setColumnWidth (0 ,100 )


        self .time_series_fit_results_table .setAlternatingRowColors (True )


        self .time_series_fit_results_table .setSortingEnabled (True )

class MainApp (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()

        self .setWindowTitle ("SD Nanopore Data Visualisation Tool")
        self .showMaximized ()



        main_widget =QWidget (self )
        self .setCentralWidget (main_widget )
        main_layout =QHBoxLayout (main_widget )

        self .left_part =QWidget (self )
        self .right_part =QWidget (self )

        self .left_layout =QVBoxLayout (self .left_part )
        self .right_layout =QVBoxLayout (self .right_part )

        main_layout .addWidget (self .left_part ,1 )
        main_layout .addWidget (self .right_part ,6 )

        title_label =QLabel ("SD Nanopore Data Visualisation Tool",self )
        author_label =QLabel ("shankar.dutt@anu.edu.au",self )
        title_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        author_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        title_label .setFont (QFont ('Arial',30 ))
        author_label .setFont (QFont ('Arial',20 ))

        self .left_layout .addWidget (title_label )
        self .left_layout .addWidget (author_label )

        self .left_tabs =QTabWidget ()
        self .right_tabs =QTabWidget ()

        self .left_layout .addWidget (self .left_tabs )
        self .right_layout .addWidget (self .right_tabs )


        self .load_data_tab =LoadDataTab (self )
        self .data_analysis_options_tab =QWidget ()
        self .visualization_settings_tab =QWidget ()

        self .left_tabs .addTab (self .load_data_tab ,"Load Data")
        self .left_tabs .addTab (self .data_analysis_options_tab ,"Data Analysis Options")
        self .left_tabs .addTab (self .visualization_settings_tab ,"Visualisation Settings")

        self .pca_controls_tab =QWidget ()
        self .left_tabs .addTab (self .pca_controls_tab ,"PCA Controls")
        self .create_pca_controls_tab ()


        self .plot_data_button =QPushButton ("Plot Data")
        self .plot_data_button .clicked .connect (self .plot_data )
        self .left_layout .addWidget (self .plot_data_button )


        self .left_tabs .currentChanged .connect (self .update_plot_button_text )



        self .plots_tab =QWidget ()
        self .pairwise_plots_tab =QWidget ()
        self .box_plots_tab =QWidget ()
        self .pca_corr_tab =QWidget ()
        self .time_series_tab =QWidget ()
        self .fit_results_tab =FitResultsTab (self )

        self .right_tabs .addTab (self .plots_tab ,"Plots")
        self .right_tabs .addTab (self .pairwise_plots_tab ,"Pairwise plots")
        self .right_tabs .addTab (self .box_plots_tab ,"Box plots and Statistics")
        self .right_tabs .addTab (self .pca_corr_tab ,"PCA and Correlation Matrix")
        self .right_tabs .addTab (self .time_series_tab ,"Time Series")
        self .right_tabs .addTab (self .fit_results_tab ,"Fit Results")
        self .corr_matrix_tab =QWidget ()
        self .right_tabs .addTab (self .corr_matrix_tab ,"Correlation Matrix")
        self .create_corr_matrix_tab ()

        self .create_menu_bar ()
        self .create_data_analysis_options ()
        self .create_visualization_settings ()
        self .create_plots_tab ()
        self .create_pairwise_plots_tab ()
        self .create_box_plots_tab ()
        self .create_pca_tab ()
        self .create_time_series_tab ()

        self .data =None 
        self .folder_path =None 
        self .file_path =None 
        self .pca_analyzer =None 

        self .last_fitted_data =None 
        self .last_fitted_params =None 
        self .fit_parameter_window =None 
        self .update_pca_button .clicked .connect (self .update_pca )
        self .pc1_combo .currentIndexChanged .connect (self .update_pca_plots )
        self .pc2_combo .currentIndexChanged .connect (self .update_pca_plots )
        for cb in self .variable_checkboxes :
            cb .stateChanged .connect (self .update_pca )
            cb .stateChanged .connect (self .update_pca_and_corr_matrix_initial )
        self .standardize_button .toggled .connect (self .update_pca )
        self .normalize_button .toggled .connect (self .update_pca )


    def plot_data (self ):
        if self .left_tabs .currentIndex ()==0 :
            selected_items =self .load_data_tab .file_list .selectedItems ()
            if selected_items :
                selected_file =selected_items [0 ].text ()
                full_path =os .path .join (self .folder_path ,selected_file )
                self .load_and_plot_data (full_path )
            else :
                QMessageBox .warning (self ,"Warning","No file selected.")
        else :
            if self .data is not None :
                self .update_all_plots ()
            else :
                selected_items =self .load_data_tab .file_list .selectedItems ()
                if selected_items :
                    selected_file =selected_items [0 ].text ()
                    full_path =os .path .join (self .folder_path ,selected_file )
                    self .load_and_plot_data (full_path )
                else :
                    QMessageBox .warning (self ,"Warning","No file selected.")


    def update_plot_button_text (self ,index ):
        if index ==0 :
            self .plot_data_button .setText ("Plot Data")
        else :
            self .plot_data_button .setText ("Update Plot")










    def validate_data (self ):
        if self .data is None :
            QMessageBox .warning (self ,"Error","No data loaded.")
            return False 
        if self .data .shape [1 ]<7 :
            QMessageBox .warning (self ,"Error",f"Insufficient number of columns. Expected at least 7, got {self .data .shape [1 ]}.")
            return False 
        return True 

    def get_data_labels (self ):
        """Return appropriate labels based on available columns"""
        base_labels =['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt']
        if self .data .shape [1 ]>7 :
            base_labels .append ('Event Baseline')
        if self .data .shape [1 ]>8 :
            base_labels .append ('Event Time')
        return base_labels 

    def update_gui_elements (self ):
        """Update GUI elements based on available columns"""
        labels =self .get_data_labels ()


        for cb ,label in zip (self .variable_checkboxes ,labels ):
            cb .setText (label )
            cb .setVisible (True )

        for cb in self .variable_checkboxes [len (labels ):]:
            cb .setVisible (False )


        has_time_data =self .data .shape [1 ]>8 
        self .enable_time_series_checkbox .setEnabled (has_time_data )
        if not has_time_data :
            self .enable_time_series_checkbox .setChecked (False )
            self .enable_time_series_checkbox .setToolTip ("Time series analysis requires event time data")
        else :
            self .enable_time_series_checkbox .setToolTip ("")

    def use_log_scale (self ):
        return self .log_scale_button .isChecked ()

    def use_log_scale_x (self ):
        return self .log_scale_x_checkbox .isChecked ()

    def use_log_scale_y (self ):
        return self .log_scale_y_checkbox .isChecked ()



    def load_and_plot_data (self ,file_path ):
        self .file_path =file_path 
        self .load_data ()
        if self .validate_data ():
            self .update_all_plots ()
        else :
            self .data =None 

    def load_data (self ):
        if self .file_path :
            self .data =self .read_file (self .file_path )
        elif self .folder_path :
            data_list =[]
            for filename in os .listdir (self .folder_path ):
                if filename .endswith ('.dataset.npz'):
                    file_path =os .path .join (self .folder_path ,filename )
                    file_data =self .read_file (file_path )
                    if file_data is not None and file_data .shape [1 ]==9 :
                        data_list .append (file_data )
            if data_list :
                self .data =np .concatenate (data_list )

        if self .data is not None and self .data .shape [1 ]!=9 :
            QMessageBox .warning (self ,"Error","Data does not have 9 columns after processing.")
            self .data =None 



    def update_all_plots (self ):
        if self .data is not None :
            self .create_plots ()
            self .create_density_plot ()
            self .update_box_plots_and_statistics ()
            self .update_pca_and_corr_matrix_initial ()
            self .update_time_series ()
            self .populate_pairwise_plots ()
            self .update_density_plot ()

    def create_menu_bar (self ):
        menu_bar =QMenuBar (self )

        file_menu =menu_bar .addMenu ('File')
        view_menu =menu_bar .addMenu ('View')
        help_menu =menu_bar .addMenu ('Help')

        select_folder_action =QAction ('Select Folder',self )
        select_folder_action .triggered .connect (self .select_folder )

        select_file_action =QAction ('Select File',self )
        select_file_action .triggered .connect (self .select_file )

        exit_action =QAction ('Exit',self )
        exit_action .triggered .connect (self .close )

        file_menu .addAction (select_folder_action )
        file_menu .addAction (select_file_action )
        file_menu .addAction (exit_action )

        about_action =QAction ('About',self )
        about_action .triggered .connect (self .about )
        help_menu .addAction (about_action )
        self .setMenuBar (menu_bar )

    def create_data_analysis_options (self ):

        content_widget =QWidget ()
        layout =QVBoxLayout (content_widget )


        standardisation_box =QGroupBox ("Choose which standardisation are you using")
        standardisation_layout =QVBoxLayout (standardisation_box )
        self .standardisation_combo_box =QComboBox ()
        self .standardisation_combo_box .addItems (['ΔI','(ΔI*I0)**0.1','(ΔI*I0)**0.5','ΔI/I0','Dutt Standardisation'])
        standardisation_layout .addWidget (self .standardisation_combo_box )
        layout .addWidget (standardisation_box )


        current_type_box =QGroupBox ("Choose type of drop in current")
        current_type_layout =QVBoxLayout (current_type_box )
        self .delta_I_button =QRadioButton ("ΔI")
        self .delta_I_fwhm_button =QRadioButton ("ΔI(fwhm)")
        current_type_button_group =QButtonGroup (self )
        current_type_button_group .addButton (self .delta_I_button )
        current_type_button_group .addButton (self .delta_I_fwhm_button )
        self .delta_I_button .setChecked (True )
        current_type_layout .addWidget (self .delta_I_button )
        current_type_layout .addWidget (self .delta_I_fwhm_button )
        layout .addWidget (current_type_box )


        dwell_time_box =QGroupBox ("Choose type of dwell time")
        dwell_time_layout =QVBoxLayout (dwell_time_box )
        self .delta_t_button =QRadioButton ("Δt")
        self .delta_t_fwhm_button =QRadioButton ("Δt(fwhm)")
        dwell_time_button_group =QButtonGroup (self )
        dwell_time_button_group .addButton (self .delta_t_button )
        dwell_time_button_group .addButton (self .delta_t_fwhm_button )
        self .delta_t_button .setChecked (True )
        dwell_time_layout .addWidget (self .delta_t_button )
        dwell_time_layout .addWidget (self .delta_t_fwhm_button )
        layout .addWidget (dwell_time_box )


        plot_type_box =QGroupBox ("Choose what to plot in the 3rd (2_1) graph and time series")
        plot_type_layout =QVBoxLayout (plot_type_box )
        self .dI_plot_button =QRadioButton ("ΔI")
        self .dt_plot_button =QRadioButton ("Δt")
        plot_type_button_group =QButtonGroup (self )
        plot_type_button_group .addButton (self .dI_plot_button )
        plot_type_button_group .addButton (self .dt_plot_button )
        self .dI_plot_button .setChecked (True )
        plot_type_layout .addWidget (self .dI_plot_button )
        plot_type_layout .addWidget (self .dt_plot_button )
        layout .addWidget (plot_type_box )


        time_series_plot_type_box =QGroupBox ("Time Series Plot Type")
        time_series_plot_type_layout =QVBoxLayout (time_series_plot_type_box )
        self .kde_button =QRadioButton ("KDE")
        self .histogram_button =QRadioButton ("Histogram")
        time_series_plot_type_group =QButtonGroup (self )
        time_series_plot_type_group .addButton (self .kde_button )
        time_series_plot_type_group .addButton (self .histogram_button )
        self .kde_button .setChecked (True )
        time_series_plot_type_layout .addWidget (self .kde_button )
        time_series_plot_type_layout .addWidget (self .histogram_button )
        layout .addWidget (time_series_plot_type_box )



        density_plot_box =QGroupBox ("Density plot options")
        density_plot_layout =QVBoxLayout (density_plot_box )
        self .density_show_checkbox =QCheckBox ("Calculate Density")
        self .density_show_checkbox .setChecked (True )
        self .gmm_button =QRadioButton ("GMM")
        self .hist2d_button =QRadioButton ("Hist2D")
        density_plot_button_group =QButtonGroup (self )
        density_plot_button_group .addButton (self .gmm_button )
        density_plot_button_group .addButton (self .hist2d_button )
        self .gmm_button .setChecked (True )
        density_plot_layout .addWidget (self .density_show_checkbox )
        density_plot_layout .addWidget (self .gmm_button )
        density_plot_layout .addWidget (self .hist2d_button )
        layout .addWidget (density_plot_box )


        density_plot_type_box =QGroupBox ("Choose what to plot in the Density Graph")
        density_plot_type_layout =QVBoxLayout (density_plot_type_box )
        self .density_dI_plot_button =QRadioButton ("ΔI vs Δt")
        self .density_area_plot_button =QRadioButton ("Area vs Δt")
        density_plot_type_button_group =QButtonGroup (self )
        density_plot_type_button_group .addButton (self .density_dI_plot_button )
        density_plot_type_button_group .addButton (self .density_area_plot_button )
        self .density_area_plot_button .setChecked (True )
        density_plot_type_layout .addWidget (self .density_dI_plot_button )
        density_plot_type_layout .addWidget (self .density_area_plot_button )
        layout .addWidget (density_plot_type_box )



        gmm_component_box =QGroupBox ("GMM components")
        gmm_component_layout =QVBoxLayout (gmm_component_box )
        self .num_components_spin_box =QSpinBox ()
        self .num_components_spin_box .setRange (1 ,10 )
        self .num_components_spin_box .setValue (4 )
        gmm_component_layout .addWidget (QLabel ("Number of components for GMM fitting:"))
        gmm_component_layout .addWidget (self .num_components_spin_box )
        layout .addWidget (gmm_component_box )


        self .data_fitting_box =QGroupBox ("Data Fitting")
        self .data_fitting_layout =QVBoxLayout (self .data_fitting_box )
        self .fitting_type_label =QLabel ("Choose fitting type:")
        self .fitting_type_combo =QComboBox ()
        self .fitting_type_combo .addItems ([
        'Gaussian','Lorentzian','Voigt','PseudoVoigt','Moffat','Pearson4',
        'Pearson7','StudentsT','BreitWigner','Lognormal','ExponentialGaussian',
        'SkewedGaussian','SkewedVoigt','ThermalDistribution','Linear','Quadratic',
        'Polynomial','Exponential','PowerLaw'
        ])
        self .show_fit_checkbox =QCheckBox ("Show Fitting")
        self .fitting_method_label =QLabel ("How to determine number of components?")
        self .fitting_method_combo =QComboBox ()
        self .fitting_method_combo .addItems (['Automatic','Given by User'])
        self .components_label =QLabel ("If not automatic, Choose number of components")
        self .components_spin_box =QSpinBox ()
        self .components_spin_box .setRange (1 ,10 )
        self .components_spin_box .setValue (3 )
        self .components_label .setVisible (False )
        self .components_spin_box .setVisible (False )



        self .polynomial_degree_label =QLabel ("Polynomial Degree:")
        self .polynomial_degree_spin_box =QSpinBox ()
        self .polynomial_degree_spin_box .setRange (1 ,10 )
        self .polynomial_degree_spin_box .setValue (2 )
        self .polynomial_degree_label .setVisible (False )
        self .polynomial_degree_spin_box .setVisible (False )

        self .show_params_button =QPushButton ("Show Fitting Parameters")

        self .data_fitting_layout .addWidget (self .fitting_type_label )
        self .data_fitting_layout .addWidget (self .fitting_type_combo )
        self .data_fitting_layout .addWidget (self .show_fit_checkbox )
        self .data_fitting_layout .addWidget (self .fitting_method_label )
        self .data_fitting_layout .addWidget (self .fitting_method_combo )
        self .data_fitting_layout .addWidget (self .components_label )
        self .data_fitting_layout .addWidget (self .components_spin_box )
        self .data_fitting_layout .addWidget (self .polynomial_degree_label )
        self .data_fitting_layout .addWidget (self .polynomial_degree_spin_box )
        self .data_fitting_layout .addWidget (self .show_params_button )
        layout .addWidget (self .data_fitting_box )


        scroll_area =QScrollArea ()
        scroll_area .setWidget (content_widget )
        scroll_area .setWidgetResizable (True )
        scroll_area .setHorizontalScrollBarPolicy (Qt .ScrollBarAlwaysOff )
        scroll_area .setVerticalScrollBarPolicy (Qt .ScrollBarAsNeeded )


        tab_layout =QVBoxLayout (self .data_analysis_options_tab )
        tab_layout .addWidget (scroll_area )


        self .connect_data_analysis_signals ()

    def connect_data_analysis_signals (self ):



















        self .fitting_type_combo .currentIndexChanged .connect (self .update_fitting_options )
        self .fitting_method_combo .currentIndexChanged .connect (self .update_fitting_options )
        self .show_params_button .clicked .connect (self .show_fitting_dialog )


    def create_data_fitting_box (self ):
        self .data_fitting_box =QGroupBox ("Data Fitting")
        self .data_fitting_layout =QVBoxLayout (self .data_fitting_box )


        self .fitting_type_label =QLabel ("Choose fitting type:")
        self .fitting_type_combo =QComboBox ()
        self .fitting_type_combo .addItems ([
        'Gaussian','Exponential Decay','Lorentzian','Polynomial',
        'Log-normal','Poisson','Sigmoidal','Power Law','Weibull',
        'Gaussian-Lorentzian'
        ])
        self .fitting_type_combo .currentIndexChanged .connect (self .update_fitting_options )


        self .fitting_method_label =QLabel ("Component determination method:")
        self .fitting_method_combo =QComboBox ()
        self .fitting_method_combo .addItems (['Automatic','Given by User'])
        self .fitting_method_combo .currentIndexChanged .connect (self .update_fitting_options )


        self .components_label =QLabel ("Number of components:")
        self .components_spin_box =QSpinBox ()
        self .components_spin_box .setRange (1 ,10 )
        self .components_spin_box .setValue (1 )


        self .polynomial_degree_label =QLabel ("Polynomial Degree:")
        self .polynomial_degree_spin_box =QSpinBox ()
        self .polynomial_degree_spin_box .setRange (1 ,10 )
        self .polynomial_degree_spin_box .setValue (2 )


        self .data_fitting_layout .addWidget (self .fitting_type_label )
        self .data_fitting_layout .addWidget (self .fitting_type_combo )
        self .data_fitting_layout .addWidget (self .fitting_method_label )
        self .data_fitting_layout .addWidget (self .fitting_method_combo )
        self .data_fitting_layout .addWidget (self .components_label )
        self .data_fitting_layout .addWidget (self .components_spin_box )
        self .data_fitting_layout .addWidget (self .polynomial_degree_label )
        self .data_fitting_layout .addWidget (self .polynomial_degree_spin_box )


        self .show_fit_checkbox =QCheckBox ("Show Fitting")
        self .show_fit_checkbox .setChecked (False )
        self .data_fitting_layout .addWidget (self .show_fit_checkbox )


        self .polynomial_degree_label =QLabel ("Polynomial Degree:")
        self .polynomial_degree_spin_box =QSpinBox ()
        self .polynomial_degree_spin_box .setRange (1 ,10 )
        self .polynomial_degree_spin_box .setValue (2 )
        self .data_fitting_layout .addWidget (self .polynomial_degree_label )
        self .data_fitting_layout .addWidget (self .polynomial_degree_spin_box )


        self .show_params_button =QPushButton ("Show Fitting Parameters")
        self .show_params_button .clicked .connect (self .show_fitting_dialog )
        self .data_fitting_layout .addWidget (self .show_params_button )



    def update_fitting_options (self ):
        fitting_type =self .fitting_type_combo .currentText ()
        fitting_method =self .fitting_method_combo .currentText ()

        self .components_spin_box .setVisible (fitting_method =='Given by User')
        self .components_label .setVisible (fitting_method =='Given by User')

        is_polynomial =fitting_type =='Polynomial'
        self .polynomial_degree_label .setVisible (is_polynomial )
        self .polynomial_degree_spin_box .setVisible (is_polynomial )


    def select_folder (self ):
        folder =QFileDialog .getExistingDirectory (self ,"Select Folder")
        if folder :
            self .folder_path =folder 
            self .file_path =None 
            self .load_data ()


    def select_file (self ):
        file ,_ =QFileDialog .getOpenFileName (self ,"Select File","","Numpy files (*.dataset.npz)")
        if file :
            self .file_path =file 
            self .folder_path =None 
            self .load_data ()

    def read_file (self ,file ):
        try :
            with np .load (file )as data :
                X =data ['X']


                if X .ndim ==1 :
                    X =X .reshape (-1 ,1 )


                if X .shape [1 ]<7 :
                    print (f"File {file } has insufficient columns: {X .shape [1 ]}")
                    return None 


                required_columns ={
                'height':0 ,
                'fwhm':1 ,
                'heightatfwhm':2 ,
                'area':3 ,
                'width':4 ,
                'skew':5 ,
                'kurt':6 
                }


                optional_columns ={
                'event_baseline_mean':7 ,
                'event_time':8 
                }


                num_rows =X .shape [0 ]
                processed_data =np .zeros ((num_rows ,9 ))


                for col_name ,col_idx in required_columns .items ():
                    processed_data [:,col_idx ]=X [:,col_idx ]


                for col_name ,col_idx in optional_columns .items ():
                    if X .shape [1 ]>col_idx :
                        processed_data [:,col_idx ]=X [:,col_idx ]
                    else :
                        if col_name =='event_baseline_mean':
                            processed_data [:,col_idx ]=np .mean (processed_data [:,:col_idx ],axis =1 )
                        elif col_name =='event_time':

                            processed_data [:,col_idx ]=np .arange (num_rows )*0.1 


                processed_data =processed_data [~np .isnan (processed_data ).any (axis =1 )]


                if processed_data .shape [0 ]==0 :
                    print (f"File {file } has no valid data after removing NaN values")
                    return None 

                print (f"Loaded {processed_data .shape [0 ]} valid rows from {file }")
                return processed_data 

        except Exception as e :
            QMessageBox .warning (self ,"Error",f"Error reading file {file }: {str (e )}")
            return None 

































    def about (self ):
        QMessageBox .about (self ,"About SD Nanopore Data Visualisation Tool",
        "\nThis application is a tool for visualise .npz data files generated from Nanosense.\n\n"
        "Author: Shankar Dutt\nEmail: shankar.dutt@anu.edu.au")

    def create_visualization_settings (self ):

        content_widget =QWidget ()
        layout =QVBoxLayout (content_widget )


        plot_type_box =QGroupBox ("Choose plot type for 2x1 plot")
        plot_type_layout =QVBoxLayout (plot_type_box )
        self .counts_button =QRadioButton ("Counts")
        self .normalised_density_button =QRadioButton ("Normalised Density")
        self .counts_button .setChecked (True )
        plot_type_layout .addWidget (self .counts_button )
        plot_type_layout .addWidget (self .normalised_density_button )
        layout .addWidget (plot_type_box )


        scale_box =QGroupBox ("Plot Scale")
        scale_layout =QVBoxLayout (scale_box )

        self .log_scale_x_checkbox =QCheckBox ("Logarithmic X-axis")
        self .log_scale_y_checkbox =QCheckBox ("Logarithmic Y-axis")

        scale_layout .addWidget (self .log_scale_x_checkbox )
        scale_layout .addWidget (self .log_scale_y_checkbox )


        plot_selection_box =QGroupBox ("Apply Log Scale to:")
        plot_selection_layout =QVBoxLayout (plot_selection_box )

        self .log_scale_plot11_checkbox =QCheckBox ("ΔI vs Δt (1x1)")
        self .log_scale_plot12_checkbox =QCheckBox ("Density Plot (1x2)")
        self .log_scale_plot21_checkbox =QCheckBox ("Histogram (2x1)")
        self .log_scale_plot22_checkbox =QCheckBox ("Area vs Δt (2x2)")

        self .log_scale_time_series_checkbox =QCheckBox ("Time Series Plots")

        plot_selection_layout .addWidget (self .log_scale_plot11_checkbox )
        plot_selection_layout .addWidget (self .log_scale_plot12_checkbox )
        plot_selection_layout .addWidget (self .log_scale_plot21_checkbox )
        plot_selection_layout .addWidget (self .log_scale_plot22_checkbox )
        plot_selection_layout .addWidget (self .log_scale_time_series_checkbox )
        scale_layout .addWidget (plot_selection_box )
        layout .addWidget (scale_box )


        plot_visibility_box =QGroupBox ("Plot Visibility")
        plot_visibility_layout =QVBoxLayout (plot_visibility_box )
        self .show_plot_11_checkbox =QCheckBox ("Show ΔI vs Δt")
        self .show_plot_12_checkbox =QCheckBox ("Show Density Plot")
        self .show_plot_21_checkbox =QCheckBox ("Show Histogram")
        self .show_plot_22_checkbox =QCheckBox ("Show Area vs Δt")
        for checkbox in [self .show_plot_11_checkbox ,self .show_plot_12_checkbox ,
        self .show_plot_21_checkbox ,self .show_plot_22_checkbox ]:
            checkbox .setChecked (True )
            plot_visibility_layout .addWidget (checkbox )
            checkbox .stateChanged .connect (self .update_plot_visibility )
        layout .addWidget (plot_visibility_box )


        colormap_box =QGroupBox ("Choose colormap for the plots")
        colormap_layout =QVBoxLayout (colormap_box )
        self .colormap_combo_box =QComboBox ()
        self .colormap_combo_box .addItems (plt .colormaps ())
        colormap_layout .addWidget (self .colormap_combo_box )
        layout .addWidget (colormap_box )


        normalization_box =QGroupBox ("Choose normalization method for the plots")
        normalization_layout =QVBoxLayout (normalization_box )
        self .linear_button =QRadioButton ("Linear")
        self .power_button =QRadioButton ("Power")
        self .log_button =QRadioButton ("Logarithmic")
        self .linear_button .setChecked (True )
        normalization_layout .addWidget (self .linear_button )
        normalization_layout .addWidget (self .power_button )
        normalization_layout .addWidget (self .log_button )
        layout .addWidget (normalization_box )


        power_box =QGroupBox ("Value of Power*10, i.e. 2 actually means 0.2")
        power_layout =QVBoxLayout (power_box )
        self .power_spin_box =QSpinBox ()
        self .power_spin_box .setRange (0 ,100 )
        self .power_spin_box .setValue (2 )
        power_layout .addWidget (self .power_spin_box )
        layout .addWidget (power_box )




        contrast_box =QGroupBox ("Adjust contrast of the density plot")
        contrast_layout =QVBoxLayout (contrast_box )
        self .min_contrast_label =QLabel ("Minimum Contrast")
        self .min_contrast_slider =QSlider (Qt .Orientation .Horizontal )
        self .min_contrast_slider .setRange (0 ,1000 )
        self .min_contrast_slider .setValue (0 )
        self .max_contrast_label =QLabel ("Maximum Contrast")
        self .max_contrast_slider =QSlider (Qt .Orientation .Horizontal )
        self .max_contrast_slider .setRange (1 ,2000 )
        self .max_contrast_slider .setValue (1000 )
        contrast_layout .addWidget (self .min_contrast_label )
        contrast_layout .addWidget (self .min_contrast_slider )
        contrast_layout .addWidget (self .max_contrast_label )
        contrast_layout .addWidget (self .max_contrast_slider )
        layout .addWidget (contrast_box )

        contrast_range_box =QGroupBox ("Contrast Slider Range")
        contrast_range_layout =QGridLayout (contrast_range_box )
        self .min_contrast_range =QSpinBox ()
        self .min_contrast_range .setRange (0 ,10000000 )
        self .min_contrast_range .setValue (0 )
        self .max_contrast_range =QSpinBox ()
        self .max_contrast_range .setRange (1 ,20000000 )
        self .max_contrast_range .setValue (1000 )
        contrast_range_layout .addWidget (QLabel ("Minimum:"),0 ,0 )
        contrast_range_layout .addWidget (self .min_contrast_range ,0 ,1 )
        contrast_range_layout .addWidget (QLabel ("Maximum:"),1 ,0 )
        contrast_range_layout .addWidget (self .max_contrast_range ,1 ,1 )
        layout .addWidget (contrast_range_box )


        self .min_contrast_range .valueChanged .connect (self .update_contrast_slider_range )
        self .max_contrast_range .valueChanged .connect (self .update_contrast_slider_range )


        bin_box =QGroupBox ("Number of Bins")
        bin_layout =QVBoxLayout (bin_box )
        self .big_plot_bins =QSpinBox ()
        self .big_plot_bins .setRange (10 ,1000 )
        self .big_plot_bins .setValue (100 )
        self .small_plot_bins =QSpinBox ()
        self .small_plot_bins .setRange (10 ,1000 )
        self .small_plot_bins .setValue (100 )
        self .markersize =QSpinBox ()
        self .markersize .setRange (1 ,1000 )
        self .markersize .setValue (40 )
        bin_layout .addWidget (QLabel ("Number of bins for plot 2x1 in Plots Tab"))
        bin_layout .addWidget (self .big_plot_bins )
        bin_layout .addWidget (QLabel ("Number of bins for small histograms in Plots Tab"))
        bin_layout .addWidget (self .small_plot_bins )
        bin_layout .addWidget (QLabel ("Size of the marker for plots 1x1 and 2x2 in Plots Tab"))
        bin_layout .addWidget (self .markersize )
        layout .addWidget (bin_box )


        time_series_box =QGroupBox ("Time Series")
        time_series_layout =QVBoxLayout (time_series_box )
        self .enable_time_series_checkbox =QCheckBox ("Enable Time Series")
        self .time_diff_spin_box =QSpinBox ()
        self .time_diff_spin_box .setRange (1 ,1000 )
        self .time_diff_spin_box .setValue (7 )
        self .time_diff_spin_box .setSuffix (" min")
        time_series_layout .addWidget (self .enable_time_series_checkbox )
        time_series_layout .addWidget (QLabel ("Split Time:"))
        time_series_layout .addWidget (self .time_diff_spin_box )
        layout .addWidget (time_series_box )


        scroll_area =QScrollArea ()
        scroll_area .setWidget (content_widget )
        scroll_area .setWidgetResizable (True )
        scroll_area .setHorizontalScrollBarPolicy (Qt .ScrollBarAlwaysOff )
        scroll_area .setVerticalScrollBarPolicy (Qt .ScrollBarAsNeeded )


        tab_layout =QVBoxLayout (self .visualization_settings_tab )
        tab_layout .addWidget (scroll_area )


        self .connect_visualization_signals ()

    def update_contrast_slider_range (self ):
            min_val =self .min_contrast_range .value ()
            max_val =self .max_contrast_range .value ()
            self .min_contrast_slider .setRange (min_val ,max_val )
            self .max_contrast_slider .setRange (min_val ,max_val )
            self .min_contrast_slider .setValue (min_val )
            self .max_contrast_slider .setValue (max_val )

    def connect_visualization_signals (self ):


        self .linear_button .toggled .connect (self .update_density_plot )
        self .power_button .toggled .connect (self .update_density_plot )
        self .power_spin_box .valueChanged .connect (self .update_density_plot )
        self .colormap_combo_box .currentIndexChanged .connect (self .update_density_plot )
        self .min_contrast_slider .valueChanged .connect (self .update_contrast )
        self .max_contrast_slider .valueChanged .connect (self .update_contrast )
        self .big_plot_bins .valueChanged .connect (self .create_plots )
        self .small_plot_bins .valueChanged .connect (self .create_plots )
        self .markersize .valueChanged .connect (self .create_plots )
        self .small_plot_bins .valueChanged .connect (self .create_density_plot )






    def update_plot_scale (self ):
        self .create_plots ()
        self .create_density_plot ()

    def update_plot_visibility (self ):
        self .canvas_11 .setVisible (self .show_plot_11_checkbox .isChecked ())
        self .canvas_12 .setVisible (self .show_plot_12_checkbox .isChecked ())
        self .canvas_21 .setVisible (self .show_plot_21_checkbox .isChecked ())
        self .canvas_22 .setVisible (self .show_plot_22_checkbox .isChecked ())

    def create_plots_tab (self ):
        plots_layout =QGridLayout (self .plots_tab )


        self .figure_11 =Figure (figsize =(8 ,6 ),constrained_layout =True )
        self .figure_12 =Figure (figsize =(8 ,6 ),constrained_layout =True )
        self .figure_21 =Figure (figsize =(8 ,6 ),constrained_layout =True )
        self .figure_22 =Figure (figsize =(8 ,6 ),constrained_layout =True )

        self .canvas_11 =FigureCanvas (self .figure_11 )
        self .canvas_12 =FigureCanvas (self .figure_12 )
        self .canvas_21 =FigureCanvas (self .figure_21 )
        self .canvas_22 =FigureCanvas (self .figure_22 )


        gs_11 =gridspec .GridSpec (4 ,4 ,figure =self .figure_11 )
        self .plot_11 =self .figure_11 .add_subplot (gs_11 [1 :,:-1 ])
        self .hist_11_top =self .figure_11 .add_subplot (gs_11 [0 ,:-1 ],sharex =self .plot_11 )
        self .hist_11_right =self .figure_11 .add_subplot (gs_11 [1 :,-1 ],sharey =self .plot_11 )
        self .hist_11_top .tick_params (axis ='x',which ='both',bottom =False ,labelbottom =False )
        self .plot_11 .tick_params (axis ='x',which ='both',bottom =True ,labelbottom =True )

        self .hist_11_right .tick_params (axis ='y',which ='both',left =False ,labelleft =False )
        self .plot_11 .tick_params (axis ='y',which ='both',left =True ,labelleft =True )
        gs_11 .update (wspace =0.02 ,hspace =0.02 )

        gs_12 =gridspec .GridSpec (4 ,3 ,width_ratios =[4 ,1.3 ,0.15 ],figure =self .figure_12 )
        self .plot_12 =self .figure_12 .add_subplot (gs_12 [1 :,0 ])
        self .hist_12_top =self .figure_12 .add_subplot (gs_12 [0 ,0 ],sharex =self .plot_12 )
        self .hist_12_right =self .figure_12 .add_subplot (gs_12 [1 :,1 ],sharey =self .plot_12 )
        self .colorbar_12_ax =self .figure_12 .add_subplot (gs_12 [1 :,2 ])
        self .hist_12_top .tick_params (axis ='x',which ='both',bottom =False ,labelbottom =False )
        self .plot_12 .tick_params (axis ='x',which ='both',bottom =True ,labelbottom =True )
        self .hist_12_right .tick_params (axis ='y',which ='both',left =False ,labelleft =False )
        self .plot_12 .tick_params (axis ='y',which ='both',left =True ,labelleft =True )
        self .plot_12 .grid (False )
        gs_12 .update (wspace =0.02 ,hspace =0.02 )


        self .plot_21 =self .figure_21 .add_subplot (111 )


        gs_22 =gridspec .GridSpec (4 ,4 ,figure =self .figure_22 )
        self .plot_22 =self .figure_22 .add_subplot (gs_22 [1 :,:-1 ])
        self .hist_22_top =self .figure_22 .add_subplot (gs_22 [0 ,:-1 ],sharex =self .plot_22 )
        self .hist_22_right =self .figure_22 .add_subplot (gs_22 [1 :,-1 ],sharey =self .plot_22 )
        self .hist_22_top .tick_params (axis ='x',which ='both',bottom =False ,labelbottom =False )
        self .plot_22 .tick_params (axis ='x',which ='both',bottom =True ,labelbottom =True )

        self .hist_22_right .tick_params (axis ='y',which ='both',left =False ,labelleft =False )
        self .plot_22 .tick_params (axis ='y',which ='both',left =True ,labelleft =True )
        gs_22 .update (wspace =0.02 ,hspace =0.02 )




        toolbar_11 =NavigationToolbar (self .canvas_11 ,self )
        toolbar_12 =NavigationToolbar (self .canvas_12 ,self )
        toolbar_21 =NavigationToolbar (self .canvas_21 ,self )
        toolbar_22 =NavigationToolbar (self .canvas_22 ,self )


        plots_layout .addWidget (self .canvas_11 ,0 ,0 )
        plots_layout .addWidget (toolbar_11 ,1 ,0 )
        plots_layout .addWidget (self .canvas_12 ,0 ,1 )
        plots_layout .addWidget (toolbar_12 ,1 ,1 )
        plots_layout .addWidget (self .canvas_21 ,2 ,0 )
        plots_layout .addWidget (toolbar_21 ,3 ,0 )
        plots_layout .addWidget (self .canvas_22 ,2 ,1 )
        plots_layout .addWidget (toolbar_22 ,3 ,1 )



    def create_plots (self ):
        if self .data is None :
            return 

        X =self .data 
        labels =['height','fwhm','heightatfwhm','area','width','skew','kurt','event_baseline_mean','event_time']

        if self .delta_I_button .isChecked ():
            delta_I =X [:,0 ]*1e3 
        else :
            delta_I =X [:,2 ]*1e3 
        if self .delta_t_button .isChecked ():
            delta_t =X [:,4 ]*1e3 
        else :
            delta_t =X [:,1 ]*1e3 

        area =X [:,3 ]

        markersize_defined =self .markersize .value ()/10 

        standard_label =self .get_standard_label ()

        def adjust_limits (data ):
            return data .min ()-(data .max ()-data .min ())/20 ,data .max ()+(data .max ()-data .min ())/20 


        if self .log_scale_x_checkbox .isChecked ():
            delta_t_plot =np .log (delta_t )
        else :
            delta_t_plot =delta_t 
        if self .log_scale_y_checkbox .isChecked ():
            delta_I_plot =np .log (delta_I )
        else :
            delta_I_plot =delta_I 


        self .plot_11 .clear ()
        self .hist_11_top .clear ()
        self .hist_11_right .clear ()

        sns .scatterplot (x =delta_t_plot ,y =delta_I_plot ,ax =self .plot_11 ,legend =False ,edgecolor =None ,s =markersize_defined ,alpha =0.5 )
        self .plot_11 .set_xlabel ('ln(Δt (ms))'if self .log_scale_x_checkbox .isChecked ()and self .log_scale_plot11_checkbox .isChecked ()else 'Δt (ms)',fontsize =14 )
        self .plot_11 .set_ylabel (f"ln({standard_label })"if self .log_scale_y_checkbox .isChecked ()and self .log_scale_plot11_checkbox .isChecked ()else standard_label ,fontsize =14 )
        self .plot_11 .set_xlim (*adjust_limits (delta_t_plot ))
        self .plot_11 .set_ylim (*adjust_limits (delta_I_plot ))

        if self .show_fit_checkbox .isChecked ():
            self .perform_fitting (delta_t_plot ,self .hist_11_top ,orientation ='vertical')
            self .perform_fitting (delta_I_plot ,self .hist_11_right ,orientation ='horizontal')
        else :
            self .plot_histograms (delta_t_plot ,self .hist_11_top ,orientation ='vertical')
            self .plot_histograms (delta_I_plot ,self .hist_11_right ,orientation ='horizontal')


        self .plot_22 .clear ()
        self .hist_22_top .clear ()
        self .hist_22_right .clear ()

        if self .log_scale_x_checkbox .isChecked ()and self .log_scale_plot22_checkbox .isChecked ():
            delta_t_area_plot =np .log (delta_t )
        else :
            delta_t_area_plot =delta_t 
        if self .log_scale_y_checkbox .isChecked ()and self .log_scale_plot22_checkbox .isChecked ():
            area_plot =np .log (area )
        else :
            area_plot =area 

        sns .scatterplot (x =delta_t_area_plot ,y =area_plot ,ax =self .plot_22 ,legend =False ,edgecolor =None ,s =markersize_defined ,alpha =0.5 )
        self .plot_22 .set_xlabel ('ln(Δt (ms))'if self .log_scale_x_checkbox .isChecked ()and self .log_scale_plot22_checkbox .isChecked ()else 'Δt (ms)',fontsize =14 )
        self .plot_22 .set_ylabel ('ln(Area)'if self .log_scale_y_checkbox .isChecked ()and self .log_scale_plot22_checkbox .isChecked ()else 'Area',fontsize =14 )
        self .plot_22 .set_xlim (*adjust_limits (delta_t_area_plot ))
        self .plot_22 .set_ylim (*adjust_limits (area_plot ))
        self .plot_histograms (delta_t_area_plot ,self .hist_22_top ,orientation ='vertical')
        self .plot_histograms (area_plot ,self .hist_22_right ,orientation ='horizontal')


        self .plot_21 .clear ()
        if self .dt_plot_button .isChecked ():
            plot_data =delta_t_plot if self .log_scale_x_checkbox .isChecked ()and self .log_scale_plot21_checkbox .isChecked ()else delta_t 
            x_label ='ln(Δt (ms))'if self .log_scale_x_checkbox .isChecked ()and self .log_scale_plot21_checkbox .isChecked ()else 'Δt (ms)'
        else :
            plot_data =np .log (delta_I )if self .log_scale_x_checkbox .isChecked ()and self .log_scale_plot21_checkbox .isChecked ()else delta_I 
            x_label =f"ln({standard_label })"if self .log_scale_x_checkbox .isChecked ()and self .log_scale_plot21_checkbox .isChecked ()else standard_label 

        if self .counts_button .isChecked ():
            if self .show_fit_checkbox .isChecked ():
                self .perform_fitting (plot_data ,self .plot_21 )
            else :
                sns .histplot (plot_data ,ax =self .plot_21 ,edgecolor =None ,bins =self .big_plot_bins .value (),linewidth =0 )
        else :
            self .plot_normalized_histogram (plot_data ,self .plot_21 )

        self .plot_21 .set_xlabel (x_label ,fontsize =14 )
        self .plot_21 .set_xlim (*adjust_limits (plot_data ))


        for fig in [self .figure_11 ,self .figure_12 ,self .figure_21 ,self .figure_22 ]:
            fig .set_constrained_layout_pads (w_pad =4 /72 ,h_pad =4 /72 ,hspace =0 ,wspace =0 )


        self .plot_11 .figure .canvas .draw ()
        self .plot_22 .figure .canvas .draw ()
        self .plot_21 .figure .canvas .draw ()
        self .plot_12 .figure .canvas .draw ()



    def plot_gmm (self ,data ,ax ,orientation ='vertical'):
        x =data 
        x_values =np .linspace (x .min (),x .max (),1000 )
        kde_values =sns .kdeplot (x ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_ydata ()
        plt .close ()

        if self .fitting_method_combo .currentText ()=='Automatic':
            kde_peaks ,_ =find_peaks (kde_values ,distance =70 ,height =0.01 )
        else :
            kde_peaks =np .zeros (self .components_spin_box .value ())

        gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (x .reshape (-1 ,1 ))
        gmm_components =[weights *norm .pdf (x_values ,loc =mean [0 ],scale =np .sqrt (covariance [0 ]))
        for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ )]

        if orientation =='vertical':
            sns .histplot (x ,bins =self .small_plot_bins .value (),kde =False ,color ='#A9A9A9',stat ="density",ax =ax ,linewidth =0 )
            for i ,component in enumerate (gmm_components ):
                ax .plot (x_values ,component ,'--',label =f'Component {i +1 }')
            ax .plot (x_values ,np .sum (gmm_components ,axis =0 ),'b-',label ='Combined GMM Fit',linewidth =2 )
            y_max =ax .get_ylim ()[1 ]
            for mean in gmm .means_ :
                ax .text (mean [0 ],y_max *0.95 ,f'{mean [0 ]:.2f}',ha ='center')
        else :
            sns .histplot (y =x ,bins =self .small_plot_bins .value (),kde =False ,color ='#A9A9A9',stat ="density",ax =ax ,linewidth =0 )
            for i ,component in enumerate (gmm_components ):
                ax .plot (component ,x_values ,'--',label =f'Component {i +1 }')
            ax .plot (np .sum (gmm_components ,axis =0 ),x_values ,'b-',label ='Combined GMM Fit',linewidth =2 )
            x_max =ax .get_xlim ()[1 ]
            for mean in gmm .means_ :
                ax .text (x_max *0.95 ,mean [0 ],f'{mean [0 ]:.2f}',va ='center')

    def plot_histograms (self ,data ,ax ,orientation ='vertical'):
        bins =self .small_plot_bins .value ()if orientation !='vertical'else self .big_plot_bins .value ()
        if orientation =='vertical':
            ax .hist (data ,edgecolor =None ,bins =bins ,linewidth =0 ,density =True )
            sns .kdeplot (data ,ax =ax )
        else :
            ax .hist (data ,edgecolor =None ,bins =bins ,linewidth =0 ,orientation ='horizontal',density =True )
            kde =sns .kdeplot (data )
            line =kde .get_lines ()[0 ]
            ax .plot (line .get_ydata (),line .get_xdata ())
            plt .close ()

    def plot_normalized_histogram (self ,data ,ax ):
        hist_counts ,bin_edges =np .histogram (data ,bins =self .big_plot_bins .value ())
        normalized_counts =hist_counts /np .max (hist_counts )
        ax .bar (bin_edges [:-1 ],normalized_counts ,align ='edge',width =np .diff (bin_edges ),edgecolor =None ,linewidth =0 )
        ax .set_ylabel ('Normalised Counts',fontsize =14 )


    def find_peaks (self ,x ,y ,threshold =0.5 ):
        from scipy .signal import find_peaks 
        peaks ,_ =find_peaks (y ,height =max (y )*threshold )
        return x [peaks ]

    def _set_initial_params (self ,params ,x ,y ,fitting_type ,peaks ):
        x_range =np .max (x )-np .min (x )
        y_range =np .max (y )-np .min (y )

        for i ,prefix in enumerate (set (p .split ('_')[0 ]for p in params )):
            peak_idx =peaks [i %len (peaks )]
            center =x [peak_idx ]
            height =y [peak_idx ]


            if i <len (peaks )-1 :
                width =(x [peaks [i +1 ]]-center )/2 
            else :
                width =(x [-1 ]-center )/2 

            params [f'{prefix }_center'].set (value =center ,min =np .min (x ),max =np .max (x ))
            params [f'{prefix }_amplitude'].set (value =height *width *np .sqrt (2 *np .pi ),min =0 )
            params [f'{prefix }_sigma'].set (value =width /2 ,min =x_range /100 ,max =x_range )

            if fitting_type in ['Voigt','PseudoVoigt','SkewedVoigt']:
                params [f'{prefix }_gamma'].set (value =width /2 ,min =0 ,max =x_range )
            elif fitting_type =='PseudoVoigt':
                params [f'{prefix }_fraction'].set (value =0.5 ,min =0 ,max =1 )
            elif fitting_type =='Moffat':
                params [f'{prefix }_beta'].set (value =1 ,min =0.5 ,max =10 )
            elif fitting_type =='Pearson4':
                params [f'{prefix }_m'].set (value =2 ,min =1.5 ,max =100 )
                params [f'{prefix }_expon'].set (value =2 ,min =0.5 ,max =10 )
                params [f'{prefix }_skew'].set (value =0 ,min =-10 ,max =10 )
            elif fitting_type =='Pearson7':
                params [f'{prefix }_expon'].set (value =1 ,min =0.5 ,max =10 )
            elif fitting_type =='ExponentialGaussian':
                params [f'{prefix }_gamma'].set (value =1 /width ,min =0 ,max =10 /x_range )
            elif fitting_type =='SkewedGaussian':
                params [f'{prefix }_gamma'].set (value =0 ,min =-10 ,max =10 )
            elif fitting_type =='StudentsT':
                params [f'{prefix }_df'].set (value =2 ,min =1 ,max =100 )
            elif fitting_type =='BreitWigner':
                params [f'{prefix }_q'].set (value =1 ,min =0.1 ,max =10 )
            elif fitting_type =='ThermalDistribution':
                params [f'{prefix }_kt'].set (value =np .mean (x ),min =0 ,max =np .max (x ))
            elif fitting_type =='Lognormal':
                log_center =np .log (np .abs (center )+1e-8 )
                params [f'{prefix }_center'].set (value =log_center ,min =np .log (np .abs (np .min (x ))+1e-8 ),max =np .log (np .abs (np .max (x ))+1e-8 ))
                params [f'{prefix }_sigma'].set (value =0.5 ,min =0.01 ,max =2 )
            elif fitting_type =='Exponential':
                params [f'{prefix }_amplitude'].set (value =np .max (y ),min =0 )
                params [f'{prefix }_decay'].set (value =1 /width ,min =0 ,max =10 /x_range )
            elif fitting_type =='PowerLaw':
                params [f'{prefix }_exponent'].set (value =-1 ,min =-10 ,max =0 )
                params [f'{prefix }_amplitude'].set (value =np .max (y )*(np .abs (center )**1 ),min =0 )

    def _create_pearson4_model (self ,x ,y ,n_components ,peaks ):
        composite_model =None 
        params =Parameters ()

        for i in range (n_components ):
            prefix =f'm{i }_'
            model =Pearson4Model (prefix =prefix )
            if composite_model is None :
                composite_model =model 
            else :
                composite_model =composite_model +model 

            peak_idx =peaks [i %len (peaks )]
            center =x [peak_idx ]
            amplitude =y [peak_idx ]


            if i <len (peaks )-1 :
                sigma =(x [peaks [i +1 ]]-center )/2 
            else :
                sigma =(x [-1 ]-center )/2 

            params .add (f'{prefix }amplitude',value =amplitude ,min =0 )
            params .add (f'{prefix }center',value =center ,min =x .min (),max =x .max ())
            params .add (f'{prefix }sigma',value =sigma ,min =0 )
            params .add (f'{prefix }m',value =2 ,min =1.5 ,max =100 )
            params .add (f'{prefix }expon',value =2 ,min =0.5 ,max =10 )
            params .add (f'{prefix }skew',value =0 ,min =-10 ,max =10 )

        return composite_model ,params 

    def fit_model (self ,x ,y ,fitting_type ,n_components ,user_params =None ):
        try :
            peaks ,_ =find_peaks (y ,height =max (y )*0.1 ,distance =len (x )//20 )

            if len (peaks )<n_components :
                print (f"Warning: Found only {len (peaks )} peaks, using {n_components } components")
                peaks =np .linspace (0 ,len (y )-1 ,n_components ).astype (int )

            if fitting_type =='Pearson4':
                model ,params =self ._create_pearson4_model (x ,y ,n_components ,peaks )
            elif fitting_type =='StudentsT':
                model ,params =setup_students_t (n_components =n_components )
            elif fitting_type =='ExponentialGaussian':
                model ,params =setup_exp_gaussian (n_components =n_components )
            elif fitting_type =='SkewedVoigt':
                model ,params =setup_skewed_voigt (n_components =n_components )
            elif fitting_type =='Linear':
                model ,params =setup_linear (n_components =n_components )
            else :
                model ,params =self ._create_general_model (x ,y ,fitting_type ,n_components ,peaks )

            if user_params :
                for param_name ,param_value in user_params .items ():
                    if param_name in params :
                        params [param_name ].set (value =float (param_value ))
                        params [param_name ].set (vary =True )

            result =self ._perform_multi_step_fitting (model ,params ,x ,y )
            return result 
        except Exception as e :
            print (f"Error in fit_model for {fitting_type }: {str (e )}")
            traceback .print_exc ()
            raise 


    def _create_general_model (self ,x ,y ,fitting_type ,n_components ,peaks ):
        models ={
        'Gaussian':GaussianModel ,
        'Lorentzian':LorentzianModel ,
        'Voigt':VoigtModel ,
        'PseudoVoigt':PseudoVoigtModel ,
        'Moffat':MoffatModel ,
        'Pearson4':Pearson4Model ,
        'Pearson7':Pearson7Model ,
        'BreitWigner':BreitWignerModel ,
        'Lognormal':LognormalModel ,
        'SkewedGaussian':SkewedGaussianModel ,
        'ThermalDistribution':ThermalDistributionModel ,
        'Quadratic':QuadraticModel ,
        'Polynomial':PolynomialModel ,
        'Exponential':ExponentialModel ,
        'PowerLaw':PowerLawModel 
        }

        if fitting_type not in models :
            raise ValueError (f"Unknown model: {fitting_type }")

        model_class =models [fitting_type ]

        if fitting_type =='Polynomial':
            return self ._create_polynomial_model (model_class ,n_components )

        composite_model =None 
        params =Parameters ()

        for i in range (n_components ):
            prefix =f'm{i }_'
            model =model_class (prefix =prefix )
            if composite_model is None :
                composite_model =model 
            else :
                composite_model =composite_model +model 


            self ._add_model_params (params ,prefix ,fitting_type ,x ,y ,peaks ,i )

        return composite_model ,params 

    def _add_model_params (self ,params ,prefix ,fitting_type ,x ,y ,peaks ,i ):
        peak_idx =peaks [i %len (peaks )]
        center =x [peak_idx ]
        height =y [peak_idx ]
        sigma =np .abs (x [1 ]-x [0 ])*5 

        params .add (f'{prefix }center',value =center ,min =np .min (x ),max =np .max (x ))
        params .add (f'{prefix }amplitude',value =height ,min =0 )
        params .add (f'{prefix }sigma',value =sigma ,min =0 )

        if fitting_type in ['Voigt','PseudoVoigt','SkewedVoigt']:
            params .add (f'{prefix }gamma',value =sigma ,min =0 )
        elif fitting_type =='Moffat':
            params .add (f'{prefix }beta',value =1 ,min =0 )
        elif fitting_type =='Pearson4':
            params .add (f'{prefix }m',value =2 ,min =1.5 ,max =100 )
            params .add (f'{prefix }expon',value =2 ,min =0.5 ,max =10 )
            params .add (f'{prefix }skew',value =0 ,min =-10 ,max =10 )
        elif fitting_type =='Pearson7':
            params .add (f'{prefix }expon',value =1 ,min =0.5 ,max =10 )
        elif fitting_type =='ExponentialGaussian':
            params .add (f'{prefix }gamma',value =1 ,min =0 )
        elif fitting_type =='SkewedGaussian':
            params .add (f'{prefix }gamma',value =0 ,min =-10 ,max =10 )
        elif fitting_type =='Quadratic':
            params .add (f'{prefix }a',value =0 )
            params .add (f'{prefix }b',value =0 )
            params .add (f'{prefix }c',value =height )
        elif fitting_type =='StudentsT':
            params .add (f'{prefix }df',value =2 ,min =1 )
        elif fitting_type =='BreitWigner':
            params .add (f'{prefix }q',value =1 )
        elif fitting_type =='ThermalDistribution':
            params .add (f'{prefix }kt',value =1 ,min =0 )
        elif fitting_type =='Lognormal':
            params .add (f'{prefix }center',value =np .log (np .abs (center )+1e-8 ),min =np .log (np .abs (np .min (x ))+1e-8 ),max =np .log (np .abs (np .max (x ))+1e-8 ))
            params .add (f'{prefix }sigma',value =0.5 ,min =0.01 ,max =2 )
        elif fitting_type =='Exponential':
            params .add (f'{prefix }decay',value =1 /(np .max (x )-np .min (x )),min =0 )
        elif fitting_type =='PowerLaw':
            params .add (f'{prefix }exponent',value =-1 ,min =-10 ,max =0 )

    def _find_peaks (self ,y ,n_components ):
        peaks ,_ =find_peaks (y ,height =max (y )*0.1 )
        if len (peaks )<n_components :

            peaks =np .linspace (0 ,len (y )-1 ,n_components ).astype (int )
        return peaks 

    def _create_polynomial_model (self ,model_class ,degree ):
        model =model_class (degree =degree ,prefix ='m0_')
        params =Parameters ()
        for i in range (degree +1 ):
            params .add (f'm0_c{i }',value =0.0 )
        return model ,params 

    def _add_common_params (self ,params ,prefix ,x ,y ,peaks ,i ):
        peak_idx =peaks [i %len (peaks )]
        center =x [peak_idx ]
        height =y [peak_idx ]
        sigma =np .abs (x [1 ]-x [0 ])*5 

        params .add (f'{prefix }center',value =center ,min =np .min (x ),max =np .max (x ))
        params .add (f'{prefix }amplitude',value =height ,min =0 )
        params .add (f'{prefix }sigma',value =sigma ,min =0 )

    def _add_model_specific_params (self ,params ,prefix ,fitting_type ,x ):
        sigma =np .abs (x [1 ]-x [0 ])*5 

        param_additions ={
        'Voigt':lambda :params .add (f'{prefix }gamma',value =sigma ,min =0 ),
        'PseudoVoigt':lambda :[params .add (f'{prefix }gamma',value =sigma ,min =0 ),
        params .add (f'{prefix }fraction',value =0.5 ,min =0 ,max =1 )],
        'Moffat':lambda :params .add (f'{prefix }beta',value =1 ,min =0 ),
        'Pearson4':lambda :[params .add (f'{prefix }m',value =1 ,min =0 ),
        params .add (f'{prefix }expon',value =1 ,min =0 ),
        params .add (f'{prefix }skew',value =0 )],
        'Pearson7':lambda :params .add (f'{prefix }expon',value =1 ,min =0 ),
        'BreitWigner':lambda :params .add (f'{prefix }q',value =1 ),
        'ThermalDistribution':lambda :params .add (f'{prefix }kt',value =1 ,min =0 ),
        'Exponential':lambda :params .add (f'{prefix }decay',value =1 /(np .max (x )-np .min (x )),min =0 ),
        'PowerLaw':lambda :params .add (f'{prefix }exponent',value =-1 ,min =-10 ,max =0 ),
        'SkewedGaussian':lambda :params .add (f'{prefix }gamma',value =sigma ,min =0 ),
        }

        if fitting_type in param_additions :
            param_additions [fitting_type ]()

    def _perform_multi_step_fitting (self ,model ,params ,x ,y ):
        result =None 
        for step in range (3 ):
            try :
                result =model .fit (y ,params ,x =x ,nan_policy ='omit')
                params =result .params 
                if result .success :
                    return result 
                else :
                    print (f"Step {step +1 }: Fit not successful. Trying again...")
                    print (f"Fit report: {result .fit_report ()}")
            except Exception as e :
                print (f"Error during fitting step {step +1 }: {str (e )}")
                traceback .print_exc ()

        if result is None :
            raise ValueError ("Fitting failed: Unable to obtain a valid result")
        else :
            print ("Warning: Fit completed but may not be optimal.")
            print (f"Final fit report: {result .fit_report ()}")
            return result 


    def guess_initial_params (self ,model ,params ,x ,y ,i ,n_components ):
        from scipy .signal import find_peaks 


        peaks ,_ =find_peaks (y ,distance =len (x )//n_components )


        if len (peaks )==0 :
            center =x [np .argmax (y )]
            amplitude =np .max (y )
            sigma =(np .max (x )-np .min (x ))/(4 *n_components )
        else :

            peak_index =peaks [min (i ,len (peaks )-1 )]
            center =x [peak_index ]
            amplitude =y [peak_index ]

            if i <len (peaks )-1 :
                sigma =(x [peaks [i +1 ]]-center )/2 
            else :
                sigma =(x [-1 ]-center )/2 

        for param_name ,param in model .make_params ().items ():
            if 'center'in param_name :
                params .add (param_name ,value =center ,min =np .min (x ),max =np .max (x ))
            elif 'sigma'in param_name or 'width'in param_name :
                params .add (param_name ,value =sigma ,min =0 )
            elif 'amplitude'in param_name :
                params .add (param_name ,value =amplitude ,min =0 )
            else :
                params .add (param_name ,value =param .value ,min =param .min ,max =param .max )

    def perform_fitting (self ,data ,ax ,orientation ='vertical'):
        x =np .sort (data )
        fitting_type =self .fitting_type_combo .currentText ()

        if self .fitting_method_combo .currentText ()=='Automatic':
            n_components =self .determine_components_auto (x )
        else :
            n_components =max (1 ,self .components_spin_box .value ())

        try :
            bins =self .small_plot_bins .value ()if orientation !='vertical'else self .big_plot_bins .value ()
            hist ,bin_edges =np .histogram (x ,bins =bins ,density =True )
            bin_centers =(bin_edges [:-1 ]+bin_edges [1 :])/2 

            result =self .fit_model (bin_centers ,hist ,fitting_type ,n_components )
            self .last_fit_result =result 
            self .last_fitted_data =x 
            self .last_fitted_params =result .params 


            n_components =self .get_number_of_components (result )

            ax .clear ()

            if orientation =='vertical':
                ax .hist (x ,bins =bins ,density =True ,alpha =0.6 ,color ='gray',label ='Data')
            else :
                ax .hist (x ,bins =bins ,density =True ,alpha =0.6 ,color ='gray',orientation ='horizontal',label ='Data')

            x_fit =np .linspace (min (x ),max (x ),1000 )
            y_fit =result .eval (x =x_fit )

            if orientation =='vertical':
                ax .plot (x_fit ,y_fit ,'r-',linewidth =2 ,label ='Overall Fit')
            else :
                ax .plot (y_fit ,x_fit ,'r-',linewidth =2 ,label ='Overall Fit')

            colors =plt .cm .rainbow (np .linspace (0 ,1 ,n_components ))
            components =result .eval_components (x =x_fit )
            for i ,(prefix ,component )in enumerate (components .items ()):
                if orientation =='vertical':
                    ax .plot (x_fit ,component ,'--',color =colors [i ],label =f'Component {i +1 }')
                else :
                    ax .plot (component ,x_fit ,'--',color =colors [i ],label =f'Component {i +1 }')

            if orientation =='vertical':
                ax .set_xlabel ('Value')
                ax .set_ylabel ('Density')
            else :
                ax .set_ylabel ('Value')
                ax .set_xlabel ('Density')

            ax .legend ()
            self .update_fit_results (result )

        except Exception as e :
            print (f"Error during {fitting_type } fitting: {str (e )}")
            traceback .print_exc ()
            self .plot_histograms (data ,ax ,orientation )

        ax .figure .canvas .draw ()


    def get_number_of_components (self ,result ):
        prefixes =set ()
        for param_name in result .params :
            prefix =param_name .split ('_')[0 ]
            prefixes .add (prefix )
        return len (prefixes )

    def update_fit_results (self ,result ):
        fit_results ={}
        n_components =self .get_number_of_components (result )

        for i in range (n_components ):
            prefix =f'm{i }_'
            component_results ={}
            for param_name ,param in result .params .items ():
                if param_name .startswith (prefix ):
                    component_results [param_name .split ('_')[-1 ]]={
                    'value':param .value ,
                    'uncertainty':param .stderr if param .stderr is not None else 'N/A'
                    }
            fit_results [f'Component {i +1 }']=component_results 


        self .components_spin_box .setValue (n_components )


        r_squared =1 -(result .residual .var ()/np .var (result .data ))


        weights =result .weights if result .weights is not None else np .ones_like (result .data )

        chi_square =np .sum (result .residual **2 /weights **2 )
        reduced_chi_square =chi_square /(len (result .data )-len (result .params ))


        self .main_graph_fit_params =result .params 

        self .fit_results_tab .update_results (fit_results ,r_squared ,chi_square ,reduced_chi_square )

        if self .fit_parameter_window :
            self .fit_parameter_window .update_params (result .params )

    def determine_components_auto (self ,x ,threshold =0.05 ):
        from scipy .stats import gaussian_kde 
        from scipy .signal import find_peaks 


        kde =gaussian_kde (x )
        x_range =np .linspace (min (x ),max (x ),1000 )
        y =kde (x_range )


        peaks ,_ =find_peaks (y ,height =max (y )*threshold ,distance =20 )


        return max (1 ,len (peaks ))


    def show_fitting_dialog (self ):
        current_params =self .get_current_fitted_params ()
        if self .fit_parameter_window is None :
            self .fit_parameter_window =FitParameterWindow (self ,current_params ,self .fitting_type_combo .currentText ())
        else :
            self .fit_parameter_window .close ()
            self .fit_parameter_window =FitParameterWindow (self ,current_params ,self .fitting_type_combo .currentText ())
        self .fit_parameter_window .show ()

    def send_to_fitting (self ,new_params ):
        if self .data is None :
            return 

        fitting_type =self .fitting_type_combo .currentText ()
        n_components =self .components_spin_box .value ()


        X =self .data 

        use_log_x =self .use_log_scale_x ()
        use_log_y =self .use_log_scale_y ()

        if self .delta_I_button .isChecked ():
            delta_I =X [:,0 ]*1e3 
        else :
            delta_I =X [:,2 ]*1e3 
        if self .delta_t_button .isChecked ():
            delta_t =X [:,4 ]*1e3 
        else :
            delta_t =X [:,1 ]*1e3 

        x_data =np .log (delta_t )if use_log_x else delta_t 
        plot_data =x_data if self .dt_plot_button .isChecked ()else delta_I 


        counts ,bin_edges =np .histogram (plot_data ,bins =self .big_plot_bins .value (),density =True )
        bin_centers =(bin_edges [:-1 ]+bin_edges [1 :])/2 

        try :

            params =Parameters ()
            for name ,value in new_params .items ():
                params .add (name ,value =value )


            result =self .fit_model (bin_centers ,counts ,fitting_type ,n_components ,user_params =params )
            self .last_fit_result =result 


            self .update_plot_with_params (result .params ,refit =False )


            self .update_fit_results (result )

            if self .fit_parameter_window :
                self .fit_parameter_window .update_params (result .params )

            QMessageBox .information (self ,"Fitting Complete","Data has been refitted with the new parameters.")
        except Exception as e :
            print (f"Error during {fitting_type } fitting: {str (e )}")
            traceback .print_exc ()
            QMessageBox .warning (self ,"Fitting Error",f"An error occurred during fitting: {str (e )}")


    def get_current_fitted_params (self ):
        if hasattr (self ,'last_fit_result'):
            fitted_params ={name :param .value for name ,param in self .last_fit_result .params .items ()}

            default_params =self .get_current_fit_params ()
            for key in default_params :
                if key not in fitted_params :
                    fitted_params [key ]=default_params [key ]
            return fitted_params 
        else :
            return self .get_current_fit_params ()

    def get_current_fit_params (self ):
        fitting_type =self .fitting_type_combo .currentText ()
        n_components =self .components_spin_box .value ()
        params ={}

        if fitting_type =='Polynomial':
            degree =self .polynomial_degree_spin_box .value ()
            for i in range (degree +1 ):
                params [f'c{i }']=0.0 
        elif fitting_type in ['Gaussian','Lorentzian','Voigt','PseudoVoigt']:
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }sigma']=1.0 
                if fitting_type in ['Voigt','PseudoVoigt']:
                    params [f'{prefix }gamma']=1.0 
        elif fitting_type in ['Moffat','Pearson7']:
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }sigma']=1.0 
                params [f'{prefix }beta']=1.0 
        elif fitting_type =='Pearson4':
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }sigma']=1.0 
                params [f'{prefix }m']=1.0 
                params [f'{prefix }skew']=0.0 
        elif fitting_type =='StudentsT':
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }sigma']=1.0 
                params [f'{prefix }df']=2.0 
        elif fitting_type =='BreitWigner':
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }sigma']=1.0 
                params [f'{prefix }q']=1.0 
        elif fitting_type =='Lognormal':
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }sigma']=1.0 
        elif fitting_type =='ExponentialGaussian':
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }sigma']=1.0 
                params [f'{prefix }gamma']=1.0 
        elif fitting_type in ['SkewedGaussian','SkewedVoigt']:
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }sigma']=1.0 
                params [f'{prefix }gamma']=0.0 
        elif fitting_type =='ThermalDistribution':
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }center']=0.0 
                params [f'{prefix }kt']=1.0 
        elif fitting_type =='Exponential':
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }decay']=1.0 
        elif fitting_type =='PowerLaw':
            for i in range (n_components ):
                prefix =f'm{i }_'
                params [f'{prefix }amplitude']=1.0 
                params [f'{prefix }exponent']=-1.0 

        return params 


    def update_plot_with_params (self ,new_params ,refit =False ):
        if self .data is None :
            return 

        X =self .data 


        use_log_x =self .use_log_scale_x ()
        use_log_y =self .use_log_scale_y ()

        if self .delta_I_button .isChecked ():
            delta_I =X [:,0 ]*1e3 
        else :
            delta_I =X [:,2 ]*1e3 
        if self .delta_t_button .isChecked ():
            delta_t =X [:,4 ]*1e3 
        else :
            delta_t =X [:,1 ]*1e3 

        x_data =np .log (delta_t )if use_log_x else delta_t 
        plot_data =x_data if self .dt_plot_button .isChecked ()else delta_I 

        fitting_type =self .fitting_type_combo .currentText ()
        n_components =self .components_spin_box .value ()


        counts ,bin_edges =np .histogram (plot_data ,bins =self .big_plot_bins .value (),density =True )
        bin_centers =(bin_edges [:-1 ]+bin_edges [1 :])/2 

        try :
            if refit :
                result =self .fit_model (bin_centers ,counts ,fitting_type ,n_components ,user_params =new_params )
                self .last_fit_result =result 
            else :
                result =self .last_fit_result 


            params =Parameters ()
            for name ,value in new_params .items ():
                params .add (name ,value =value )


            x_fit =np .linspace (np .min (plot_data ),np .max (plot_data ),1000 )
            y_fit =result .eval (x =x_fit ,params =params )


            self .plot_21 .clear ()
            self .plot_21 .hist (plot_data ,bins =self .big_plot_bins .value (),density =True ,alpha =0.7 ,label ='Data')
            self .plot_21 .plot (x_fit ,y_fit ,'r-',label ='Updated Fit')

            x_label ='log(Δt (ms))'if use_log_x and self .dt_plot_button .isChecked ()else 'Δt (ms)'if self .dt_plot_button .isChecked ()else self .get_standard_label ()
            self .plot_21 .set_xlabel (x_label ,fontsize =14 )
            self .plot_21 .set_ylabel ('Density',fontsize =14 )
            self .plot_21 .set_title (f'{fitting_type } Fit')


            colors =plt .cm .rainbow (np .linspace (0 ,1 ,n_components ))
            components =result .eval_components (x =x_fit ,params =params )
            for i ,(prefix ,component )in enumerate (components .items ()):
                self .plot_21 .plot (x_fit ,component ,'--',color =colors [i ],label =f'Component {i +1 }')

            self .plot_21 .legend ()
            self .plot_21 .set_xlim (np .min (plot_data ),np .max (plot_data ))


            self .plot_21 .figure .canvas .draw ()

            if refit :
                self .update_fit_results (result )

        except Exception as e :
            print (f"Error during {fitting_type } fitting: {str (e )}")
            traceback .print_exc ()
            QMessageBox .warning (self ,"Fitting Error",f"An error occurred during fitting: {str (e )}")


    def plot_fit_components (self ,x ,x_values ,components ,ax ,orientation ):
        if orientation =='vertical':
            ax .hist (x ,bins =self .small_plot_bins .value (),density =True ,alpha =0.7 ,orientation ='vertical')
            for i ,component in enumerate (components ):
                ax .plot (x_values ,component ,'--',label =f'Component {i +1 }')
            ax .plot (x_values ,np .sum (components ,axis =0 ),'r-',label ='Combined Fit',linewidth =2 )
        else :
            ax .hist (x ,bins =self .small_plot_bins .value (),density =True ,alpha =0.7 ,orientation ='horizontal')
            for i ,component in enumerate (components ):
                ax .plot (component ,x_values ,'--',label =f'Component {i +1 }')
            ax .plot (np .sum (components ,axis =0 ),x_values ,'r-',label ='Combined Fit',linewidth =2 )



    def label_peaks (self ,ax ,components ,x_values ,orientation ):
        combined =np .sum (components ,axis =0 )
        peaks ,_ =find_peaks (combined )
        peak_x =x_values [peaks ]
        peak_y =combined [peaks ]

        if orientation =='vertical':
            y_max =ax .get_ylim ()[1 ]
            for x ,y in zip (peak_x ,peak_y ):
                ax .text (x ,y_max *0.95 ,f'{x :.2f}',ha ='center')
        else :
            x_max =ax .get_xlim ()[1 ]
            for x ,y in zip (peak_y ,peak_x ):
                ax .text (x_max *0.95 ,y ,f'{y :.2f}',va ='center')


    def get_standard_label (self ):
        standardisation =self .standardisation_combo_box .currentText ()
        if standardisation =='ΔI':
            return 'ΔI (pA)'
        elif standardisation =='(ΔI*I0)**0.1':
            return '$(ΔI \u00D7 I_0)^{0.1}$'
        elif standardisation =='(ΔI*I0)**0.5':
            return '$(ΔI \u00D7 I_0)^{0.5}$'
        elif standardisation =='ΔI/I0':
            return '$ΔI/I_0$'
        elif standardisation =='Dutt Standardisation':
            return 'ΔI (pA) (Dutt Standardised)'
        else :
            return 'ΔI (pA)'


    def create_density_plot (self ):
        try :
            self .plot_12 .clear ()
            self .colorbar_12_ax .clear ()

            X =self .data 

            if self .delta_t_button .isChecked ():
                x =X [:,4 ]*1e3 
            else :
                x =X [:,1 ]*1e3 

            if self .log_scale_x_checkbox .isChecked ()and self .log_scale_plot12_checkbox .isChecked ():
                x =np .log (x )

            if self .density_area_plot_button .isChecked ():
                y =X [:,3 ]
                density_y_label ="Area"
            else :
                if self .delta_I_button .isChecked ():
                    y =X [:,0 ]*1e3 
                else :
                    y =X [:,2 ]*1e3 
                density_y_label ="ΔI (pA)"

            if self .log_scale_y_checkbox .isChecked ()and self .log_scale_plot12_checkbox .isChecked ():
                y =np .log (y )

            if self .gmm_button .isChecked ():
                gmm =GaussianMixture (n_components =self .num_components_spin_box .value ()).fit (np .vstack ([x ,y ]).T )
                X ,Y =np .meshgrid (np .linspace (np .min (x ),np .max (x ),1000 ),np .linspace (np .min (y ),np .max (y ),1000 ))
                XX =np .array ([X .ravel (),Y .ravel ()]).T 
                Z =gmm .score_samples (XX )
                Z =Z .reshape (X .shape )
                Z =np .exp (Z )

                self .current_density_image =self .plot_12 .imshow (Z ,aspect ='auto',origin ='lower',
                extent =[x .min (),x .max (),y .min (),y .max ()],
                cmap =self .colormap_combo_box .currentText (),
                norm =self .get_norm (Z ))
            else :
                H ,xedges ,yedges =np .histogram2d (x ,y ,bins =100 ,density =True )
                X ,Y =np .meshgrid (xedges [:-1 ],yedges [:-1 ])
                self .current_density_image =self .plot_12 .pcolormesh (X ,Y ,H .T ,
                cmap =self .colormap_combo_box .currentText (),
                norm =self .get_norm (H ))

            self .plot_12 .figure .colorbar (mappable =self .current_density_image ,ax =self .plot_12 ,cax =self .colorbar_12_ax )
            self .plot_12 .set_xlabel ('log(Δt (ms))'if self .log_scale_x_checkbox .isChecked ()else 'Δt (ms)',fontsize =14 )
            self .plot_12 .set_ylabel (f"log({density_y_label })"if self .log_scale_y_checkbox .isChecked ()else density_y_label ,fontsize =14 )
            self .plot_12 .set_xlim ([np .min (x ),np .max (x )])
            self .plot_12 .set_ylim ([np .min (y ),np .max (y )])
            self .plot_12 .grid (False )

            self .hist_12_top .clear ()
            self .hist_12_right .clear ()
            self .plot_histograms (x ,self .hist_12_top ,orientation ='vertical')
            self .plot_histograms (y ,self .hist_12_right ,orientation ='horizontal')

            self .plot_12 .figure .canvas .draw ()
        except Exception as e :
            QMessageBox .warning (self ,"Warning",f"Error in creating density plot: {str (e )}")

    def update_contrast (self ):
        min_val =self .min_contrast_slider .value ()/1000.0 
        max_val =self .max_contrast_slider .value ()/1000.0 


        min_range =self .min_contrast_range .value ()/1000.0 
        max_range =self .max_contrast_range .value ()/1000.0 


        min_val =min_range +(max_range -min_range )*min_val 
        max_val =min_range +(max_range -min_range )*max_val 

        self .current_density_image .set_clim (min_val ,max_val )
        self .plot_12 .figure .canvas .draw ()


    def get_norm (self ,data_array =None ):
        try :
            if data_array is None :
                data_array =self .current_density_image .get_array ()

            if self .linear_button .isChecked ():
                return None 
            elif self .power_button .isChecked ():
                power =self .power_spin_box .value ()
                return PowerNorm (power /10 )
            elif self .log_button .isChecked ():
                return LogNorm ()
        except :
            QMessageBox .warning (self ,"Warning","There is nothing plotted!")
            pass 

    def update_density_plot (self ):

        try :
            norm =self .get_norm ()


            self .current_density_image .set_norm (norm )
            self .current_density_image .set_cmap (self .colormap_combo_box .currentText ())


            self .colorbar_12_ax .clear ()
            self .plot_12 .figure .colorbar (mappable =self .current_density_image ,ax =self .plot_12 ,cax =self .colorbar_12_ax )

            self .plot_12 .figure .canvas .draw ()
        except :
            QMessageBox .warning (self ,"Warning","There is nothing plotted!")
            pass 

    def create_pairwise_plots_tab (self ):
        """Set up the layout for pairwise plots"""

        pairwise_plots_layout =QVBoxLayout (self .pairwise_plots_tab )


        self .pairwise_plots_figure ,self .pairwise_plots_axes =plt .subplots (9 ,9 ,figsize =(18 ,18 ),dpi =80 )

        self .pairwise_plots_canvas =FigureCanvas (self .pairwise_plots_figure )


        pairwise_plots_toolbar =NavigationToolbar (self .pairwise_plots_canvas ,self )


        pairwise_plots_layout .addWidget (self .pairwise_plots_canvas )
        pairwise_plots_layout .addWidget (pairwise_plots_toolbar )


        self .pairwise_plots_canvas .mpl_connect ('button_press_event',self .on_pairwise_plot_clicked )


    def populate_pairwise_plots (self ):
        if self .data is None :
            return 

        X =self .data 
        labels =['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt','Event Baseline','Event Time']

        axis_limits =[(min (X [:,i ])-0.1 *(max (X [:,i ])-min (X [:,i ])),
        max (X [:,i ])+0.1 *(max (X [:,i ])-min (X [:,i ])))for i in range (9 )]

        for i in range (9 ):
            for j in range (9 ):
                ax =self .pairwise_plots_axes [i ][j ]
                ax .clear ()

                x_data =X [:,j ]
                y_data =X [:,i ]

                x_ticks =np .linspace (axis_limits [j ][0 ],axis_limits [j ][1 ],6 )
                y_ticks =np .linspace (axis_limits [i ][0 ],axis_limits [i ][1 ],6 )

                ax .hlines (y_ticks ,xmin =axis_limits [j ][0 ],xmax =axis_limits [j ][1 ],
                colors ='grey',linestyles ='--',linewidth =0.5 )
                ax .vlines (x_ticks ,ymin =axis_limits [i ][0 ],ymax =axis_limits [i ][1 ],
                colors ='grey',linestyles ='--',linewidth =0.5 )

                if i ==j :
                    ax .hist (x_data ,bins =100 ,edgecolor ='k',color ='gray')
                    ax .set_xlim (axis_limits [j ])
                else :
                    ax .scatter (x_data ,y_data ,s =5 )
                    ax .set_xlim (axis_limits [j ])
                    ax .set_ylim (axis_limits [i ])

                if j ==0 :
                    ax .set_ylabel (labels [i ],fontsize =12 )
                else :
                    ax .set_yticks ([])

                if i ==8 :
                    ax .set_xlabel (labels [j ],fontsize =12 )
                else :
                    ax .set_xticks ([])


        self .pairwise_plots_figure .tight_layout ()
        self .pairwise_plots_figure .tight_layout ()
        self .pairwise_plots_canvas .draw ()
        self .pairwise_plots_figure .tight_layout ()




    def on_pairwise_plot_clicked (self ,event ):
        if event .inaxes :
            for i ,ax_row in enumerate (self .pairwise_plots_axes ):
                for j ,ax in enumerate (ax_row ):
                    if ax ==event .inaxes :
                        self .show_popup (i ,j )
                        return 

    def show_popup (self ,row ,col ):
        if self .data is None :
            return 

        labels =['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt','Event Baseline','Event Time']
        variable_a =labels [row ]
        variable_b =labels [col ]

        popup =QMainWindow (self )
        if row ==col :
            popup .setWindowTitle (f'Plot: {variable_a } Histogram')
        else :
            popup .setWindowTitle (f'Plot: {variable_a } vs {variable_b }')
        popup .setGeometry (200 ,200 ,600 ,400 )
        layout =QVBoxLayout ()


        fig ,ax =plt .subplots (figsize =(6 ,4 ))
        canvas =FigureCanvas (fig )
        layout .addWidget (canvas )


        toolbar =NavigationToolbar (canvas ,popup )
        layout .addWidget (toolbar )

        widget =QWidget ()
        widget .setLayout (layout )
        popup .setCentralWidget (widget )

        X =self .data 


        x_data =X [:,col ]
        y_data =X [:,row ]

        if row ==col :
            ax .hist (x_data ,bins =100 ,edgecolor ='k',color ='gray')
        else :
            ax .scatter (x_data ,y_data ,s =7 )

        ax .set_xlabel (variable_b )
        if row ==col :
            ax .set_ylabel ("Counts")
        else :
            ax .set_ylabel (variable_a )

        canvas .draw ()
        popup .show ()


    def create_box_plots_tab (self ):

        box_plots_layout =QVBoxLayout (self .box_plots_tab )


        splitter =QSplitter (Qt .Orientation .Vertical )


        self .box_plots_figure =Figure (figsize =(10 ,7.5 ))
        self .box_plots_canvas =FigureCanvas (self .box_plots_figure )


        box_plot_container =QWidget ()
        box_plot_layout =QVBoxLayout (box_plot_container )


        box_plots_toolbar =NavigationToolbar (self .box_plots_canvas ,self )


        box_plot_layout .addWidget (self .box_plots_canvas )
        box_plot_layout .addWidget (box_plots_toolbar )


        splitter .addWidget (box_plot_container )


        self .statistics_table =QTableWidget ()


        splitter .addWidget (self .statistics_table )


        splitter .setSizes ([750 ,250 ])


        box_plots_layout .addWidget (splitter )

    def update_box_plots_and_statistics (self ):
        if self .data is None :
            return 


        X =self .data 


        variables =[X [:,i ]for i in range (9 )]
        labels =['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt','Event Baseline','Event Time']


        self .box_plots_figure .clear ()
        axes =self .box_plots_figure .subplots (2 ,4 )

        for i ,(ax ,variable ,label )in enumerate (zip (axes .flatten (),variables ,labels )):
            ax .boxplot (variable )
            ax .set_title (label )


        axes [1 ,3 ].axis ('off')


        self .box_plots_canvas .draw ()


        statistics =[]
        for variable in variables :
            mean =np .mean (variable )
            median =np .median (variable )
            variance =np .var (variable )
            std_dev =np .std (variable )
            minimum =np .min (variable )
            maximum =np .max (variable )
            range_val =maximum -minimum 
            coef_var =(std_dev /mean )if mean !=0 else 0 
            q25 =np .percentile (variable ,25 )
            q75 =np .percentile (variable ,75 )

            statistics .append ([mean ,median ,variance ,std_dev ,minimum ,maximum ,range_val ,coef_var ,q25 ,q75 ])


        self .statistics_table .setRowCount (len (variables ))
        self .statistics_table .setColumnCount (10 )
        self .statistics_table .setHorizontalHeaderLabels (['Mean','Median','Variance','Std. Dev.','Min','Max','Range','Coef. Var.','Q25','Q75'])
        self .statistics_table .setVerticalHeaderLabels (labels )


        header =self .statistics_table .horizontalHeader ()
        header .setSectionResizeMode (QHeaderView .ResizeMode .Stretch )


        for i ,stats in enumerate (statistics ):
            for j ,stat in enumerate (stats ):
                self .statistics_table .setItem (i ,j ,QTableWidgetItem (str (round (stat ,8 ))))

    def create_pca_controls_tab (self ):
        layout =QVBoxLayout (self .pca_controls_tab )


        component_group =QGroupBox ("Select Principal Components")
        component_layout =QHBoxLayout ()
        self .pc1_combo =QComboBox ()
        self .pc2_combo =QComboBox ()
        for i in range (1 ,10 ):
            self .pc1_combo .addItem (f"PC{i }")
            self .pc2_combo .addItem (f"PC{i }")
        self .pc1_combo .setCurrentIndex (0 )
        self .pc2_combo .setCurrentIndex (1 )
        component_layout .addWidget (QLabel ("X-axis:"))
        component_layout .addWidget (self .pc1_combo )
        component_layout .addWidget (QLabel ("Y-axis:"))
        component_layout .addWidget (self .pc2_combo )
        component_group .setLayout (component_layout )
        layout .addWidget (component_group )


        variable_group =QGroupBox ("Select Variables for PCA")
        variable_layout =QVBoxLayout ()
        self .variable_checkboxes =[]
        for var in ['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt','Event Baseline','Event Time']:
            cb =QCheckBox (var )
            cb .setChecked (True )
            self .variable_checkboxes .append (cb )
            variable_layout .addWidget (cb )
        variable_group .setLayout (variable_layout )
        layout .addWidget (variable_group )


        preprocess_group =QGroupBox ("Data Preprocessing")
        preprocess_layout =QHBoxLayout ()
        self .standardize_button =QRadioButton ("Standardize")
        self .normalize_button =QRadioButton ("Normalize")
        self .standardize_button .setChecked (True )
        preprocess_layout .addWidget (self .standardize_button )
        preprocess_layout .addWidget (self .normalize_button )
        preprocess_group .setLayout (preprocess_layout )
        layout .addWidget (preprocess_group )


        marker_size_group =QGroupBox ("Marker Size")
        marker_size_layout =QHBoxLayout ()
        self .marker_size_slider =QSlider (Qt .Orientation .Horizontal )
        self .marker_size_slider .setRange (1 ,100 )
        self .marker_size_slider .setValue (7 )
        self .marker_size_label =QLabel ("7")
        self .marker_size_slider .valueChanged .connect (self .update_marker_size_label )
        marker_size_layout .addWidget (self .marker_size_slider )
        marker_size_layout .addWidget (self .marker_size_label )
        marker_size_group .setLayout (marker_size_layout )
        layout .addWidget (marker_size_group )


        variance_group =QGroupBox ("Show Variance")
        variance_layout =QVBoxLayout ()
        self .show_variance_checkbox =QCheckBox ("Show Variance")
        self .show_variance_checkbox .stateChanged .connect (self .update_pca )
        variance_layout .addWidget (self .show_variance_checkbox )
        self .variance_variable_combo =QComboBox ()
        self .variance_variable_combo .addItems (['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt','Event Baseline','Event Time'])
        self .variance_variable_combo .currentIndexChanged .connect (self .update_pca )
        variance_layout .addWidget (self .variance_variable_combo )
        variance_group .setLayout (variance_layout )
        layout .addWidget (variance_group )


        self .update_pca_button =QPushButton ("Update PCA")
        self .update_pca_button .clicked .connect (self .update_pca )
        layout .addWidget (self .update_pca_button )
        self .standardize_button .toggled .connect (self .update_pca )
        self .normalize_button .toggled .connect (self .update_pca )

    def select_all_variables (self ):
        for cb in self .variable_checkboxes :
            cb .setChecked (True )

    def deselect_all_variables (self ):
        for cb in self .variable_checkboxes :
            cb .setChecked (False )

    def on_pca_type_changed (self ,pca_type ):
        self .kernel_type_combo .setVisible (pca_type =="Kernel PCA")

    def update_component_slider_label (self ,value ):
        self .component_slider_label .setText (str (value ))

    def update_pca (self ):
        if self .data is None :
            return 


        selected_vars =[i for i ,cb in enumerate (self .variable_checkboxes )if cb .isChecked ()]
        data =self .data [:,selected_vars ]


        preprocess_method ='standardize'if self .standardize_button .isChecked ()else 'normalize'


        self .pca_analyzer =PCAAnalyzer ()
        pca_result =self .pca_analyzer .perform_pca (data ,len (selected_vars ),preprocess_method =preprocess_method )
        self .pca_analyzer .data =data 


        self .update_pca_plots ()


        self .update_pca_results (self .pca_analyzer .pca ,self .pca_analyzer .data )

    def create_corr_matrix_tab (self ):
        layout =QVBoxLayout (self .corr_matrix_tab )

        self .corr_matrix_figure =Figure (figsize =(8 ,6 ))
        self .corr_matrix_canvas =FigureCanvas (self .corr_matrix_figure )
        layout .addWidget (self .corr_matrix_canvas )

        corr_matrix_toolbar =NavigationToolbar (self .corr_matrix_canvas ,self )
        layout .addWidget (corr_matrix_toolbar )

    def update_corr_matrix (self ):
        if self .data is None :
            return 

        selected_vars =[i for i ,cb in enumerate (self .variable_checkboxes )if cb .isChecked ()]
        data =self .data [:,selected_vars ]
        labels =[cb .text ()for cb in self .variable_checkboxes if cb .isChecked ()]

        corr_matrix =np .corrcoef (data .T )

        self .corr_matrix_figure .clear ()
        ax =self .corr_matrix_figure .add_subplot (111 )
        sns .heatmap (corr_matrix ,annot =True ,ax =ax ,cmap ='coolwarm',xticklabels =labels ,yticklabels =labels )
        ax .set_title ('Correlation Matrix')

        self .corr_matrix_canvas .draw ()


    def update_pca_plots (self ):

        if self .pca_analyzer is None or not isinstance (self .pca_analyzer .transformed_data ,np .ndarray ):
            print ("PCA data is not available or not in the correct format")
            return 

        self .pca_figure .clear ()

        pc1 =int (self .pc1_combo .currentText ()[2 :])-1 
        pc2 =int (self .pc2_combo .currentText ()[2 :])-1 

        transformed_data =self .pca_analyzer .transformed_data 

        if self .pca_2d_button .isChecked ():
            ax =self .pca_figure .add_subplot (111 )
            scatter =ax .scatter (transformed_data [:,pc1 ],transformed_data [:,pc2 ],
            s =self .marker_size_slider .value ())
            ax .set_xlabel (f"PC{pc1 +1 }")
            ax .set_ylabel (f"PC{pc2 +1 }")

            if self .show_variance_checkbox .isChecked ():
                var_index =self .variance_variable_combo .currentIndex ()
                original_data =self .pca_analyzer .data [:,var_index ]
                scatter .set_array (original_data )
                self .pca_figure .colorbar (scatter ,label =self .variance_variable_combo .currentText ())
        else :
            ax =self .pca_figure .add_subplot (111 ,projection ='3d')
            scatter =ax .scatter (transformed_data [:,pc1 ],transformed_data [:,pc2 ],transformed_data [:,2 ],
            s =self .marker_size_slider .value ())
            ax .set_xlabel (f"PC{pc1 +1 }")
            ax .set_ylabel (f"PC{pc2 +1 }")
            ax .set_zlabel ("PC3")

            if self .show_variance_checkbox .isChecked ():
                var_index =self .variance_variable_combo .currentIndex ()
                original_data =self .pca_analyzer .data [:,var_index ]
                scatter .set_array (original_data )
                self .pca_figure .colorbar (scatter ,label =self .variance_variable_combo .currentText ())

        self .pca_canvas .draw ()

    def update_marker_size_label (self ,value ):
        self .marker_size_label .setText (str (value ))

    def update_pca_results (self ,pca ,data_scaled ):
        explained_variance =pca .explained_variance_ratio_ 
        feature_contributions =pca .components_ 
        kmo_value =self .calculate_kmo_test (data_scaled )

        results_text ="PCA Results:\n\n"
        results_text +="What is PCA?\n"
        results_text +="PCA (Principal Component Analysis) is a powerful statistical technique used to simplify complex datasets. "
        results_text +="It works by identifying the main patterns or 'components' in your data, effectively reducing its dimensionality "
        results_text +="while preserving as much information as possible. Think of it as finding the most important dimensions in your data, "
        results_text +="allowing you to focus on what matters most.\n\n"

        results_text +="How does PCA work?\n"
        results_text +="1. PCA starts by standardizing your data to ensure all variables are on the same scale.\n"
        results_text +="2. It then calculates the covariance matrix to understand how variables relate to each other.\n"
        results_text +="3. From this matrix, PCA computes 'eigenvectors' and 'eigenvalues'. The eigenvectors become your new principal components, "
        results_text +="   while the eigenvalues tell you how much variance each component explains.\n"
        results_text +="4. Finally, PCA ranks these components by importance (i.e., how much variance they explain) and selects the top ones.\n\n"


        results_text +="Explained Variance Ratio:\n"
        results_text +="This ratio tells us the proportion of the dataset's variability that each principal component accounts for.\n"
        cumulative_variance =0 
        for i ,ratio in enumerate (explained_variance ):
            cumulative_variance +=ratio 
            results_text +=f"PC{i +1 }: {ratio :.2%} (Cumulative: {cumulative_variance :.2%})\n"
            if i ==0 :
                results_text +="  This is the most important dimension, capturing the largest amount of variability in your data.\n"
            elif i ==1 :
                results_text +="  This is the second most important dimension, orthogonal to PC1, capturing the next largest amount of variability.\n"
            elif i ==2 :
                results_text +="  This captures additional patterns in the data, orthogonal to both PC1 and PC2.\n"
            elif i ==len (explained_variance )-1 :
                results_text +="  This is the last component, usually capturing the least amount of variability (often noise).\n"


        results_text +="\nWhat does this mean?\n"
        results_text +=f"The first component (PC1) explains {explained_variance [0 ]:.2%} of the total variance in your data. "
        results_text +=f"Together, the first two components explain {(explained_variance [0 ]+explained_variance [1 ]):.2%} of the variance.\n"
        results_text +=f"To retain 95% of the variance in your data, you would need to keep the first {next (i for i ,cv in enumerate (np .cumsum (explained_variance ))if cv >=0.95 )+1 } principal components.\n\n"

        results_text +="Feature Contributions:\n"
        results_text +="This shows how much each original variable contributes to each principal component. "
        results_text +="These contributions are also known as 'loadings' or 'eigenvectors'.\n"
        results_text +="A larger absolute value (positive or negative) means that variable is more important for that component.\n"
        results_text +="The sign indicates the direction of the relationship:\n"
        results_text +="  - Positive: As the variable increases, the component score increases.\n"
        results_text +="  - Negative: As the variable increases, the component score decreases.\n\n"

        selected_vars =[cb .text ()for cb in self .variable_checkboxes if cb .isChecked ()]
        for i ,pc in enumerate (feature_contributions ):
            results_text +=f"PC{i +1 }:\n"
            sorted_contributions =sorted (zip (selected_vars ,pc ),key =lambda x :abs (x [1 ]),reverse =True )
            for var ,contrib in sorted_contributions [:3 ]:
                results_text +=f"  {var }: {contrib :.3f}\n"
            results_text +=f"  Interpretation: PC{i +1 } primarily represents variations in {sorted_contributions [0 ][0 ]} and {sorted_contributions [1 ][0 ]}.\n"
            results_text +=f"  A high score in PC{i +1 } likely indicates {'high'if sorted_contributions [0 ][1 ]>0 else 'low'} {sorted_contributions [0 ][0 ]} "
            results_text +=f"and {'high'if sorted_contributions [1 ][1 ]>0 else 'low'} {sorted_contributions [1 ][0 ]}.\n\n"

        results_text +="Kaiser-Meyer-Olkin (KMO) Test:\n"
        if kmo_value is not None :
            results_text +=f"KMO value: {kmo_value :.3f} - {interpret_kmo (kmo_value )}\n"
            results_text +="The KMO test measures the sampling adequacy for each variable in your model and for the complete model. "
            results_text +="It indicates the proportion of variance in your variables that might be caused by underlying factors.\n"
            results_text +=f"A value of {kmo_value :.3f} is considered {interpret_kmo (kmo_value ).lower ()}, "
            if kmo_value >=0.6 :
                results_text +="which suggests that PCA is likely to be useful for your data.\n"
        else :
            results_text +="KMO test could not be performed due to statistical issues with the data.\n"
            results_text +="This could be due to high multicollinearity or insufficient observations.\n"
            results_text +="Consider reducing the number of variables or increasing the sample size.\n"

        results_text +="\nHow to use these results:\n"
        results_text +="1. Dimensionality Reduction: You could use just the first few PCs to represent your data, simplifying further analyses.\n"
        results_text +="2. Feature Selection: Variables with high contributions to important PCs are your most informative features.\n"
        results_text +="3. Data Visualization: Plot your data using the first 2-3 PCs as axes to visualize the main patterns.\n"
        results_text +="4. Noise Reduction: Later PCs often represent noise; removing them can clean your data.\n"
        results_text +="5. Understanding Relationships: PCA can reveal hidden relationships between your variables.\n"

        self .pca_results_text .setText (results_text )

    def create_pca_tab (self ):
        pca_corr_layout =QVBoxLayout (self .pca_corr_tab )


        self .pca_figure =Figure (figsize =(8 ,6 ))
        self .pca_canvas =FigureCanvas (self .pca_figure )
        pca_corr_layout .addWidget (self .pca_canvas )


        pca_toolbar =NavigationToolbar (self .pca_canvas ,self )
        pca_corr_layout .addWidget (pca_toolbar )


        plot_type_layout =QHBoxLayout ()
        self .pca_2d_button =QRadioButton ("2D Plot")
        self .pca_3d_button =QRadioButton ("3D Plot")
        self .pca_2d_button .setChecked (True )
        plot_type_layout .addWidget (self .pca_2d_button )
        plot_type_layout .addWidget (self .pca_3d_button )
        pca_corr_layout .addLayout (plot_type_layout )


        self .pca_results_text =QTextEdit ()
        self .pca_results_text .setReadOnly (True )
        pca_corr_layout .addWidget (self .pca_results_text )


        clustering_layout =QHBoxLayout ()
        self .cluster_button =QPushButton ("Perform K-means Clustering")
        self .cluster_button .clicked .connect (self .perform_clustering )
        self .n_clusters_input =QSpinBox ()
        self .n_clusters_input .setMinimum (2 )
        self .n_clusters_input .setMaximum (10 )
        self .n_clusters_input .setValue (3 )
        clustering_layout .addWidget (QLabel ("Number of clusters:"))
        clustering_layout .addWidget (self .n_clusters_input )
        clustering_layout .addWidget (self .cluster_button )
        pca_corr_layout .addLayout (clustering_layout )






    def perform_clustering (self ):
        if self .pca_analyzer is None or self .pca_analyzer .transformed_data is None :
            return 

        n_clusters =self .n_clusters_input .value ()
        cluster_labels =self .pca_analyzer .perform_clustering (n_clusters )


        self .pca_figure .clear ()
        ax =self .pca_figure .add_subplot (111 )
        scatter =ax .scatter (self .pca_analyzer .transformed_data [:,0 ],
        self .pca_analyzer .transformed_data [:,1 ],
        c =cluster_labels ,cmap ='viridis')
        ax .set_xlabel (f"PC{self .pc1_combo .currentText ()}")
        ax .set_ylabel (f"PC{self .pc2_combo .currentText ()}")
        self .pca_figure .colorbar (scatter ,label ='Cluster')
        self .pca_canvas .draw ()


        cluster_sizes =[sum (cluster_labels ==i )for i in range (n_clusters )]
        cluster_info ="Clustering Results:\n"
        for i ,size in enumerate (cluster_sizes ):
            cluster_info +=f"Cluster {i +1 }: {size } points\n"
        self .pca_results_text .append (cluster_info )

    def project_new_data (self ):
        if self .pca_analyzer is None or self .pca_analyzer .pca is None :
            return 

        dialog =NewDataDialog (self ,n_features =len (self .variable_checkboxes ))
        if dialog .exec ():
            new_data =np .array (dialog .get_data ()).reshape (1 ,-1 )
            projected_data =self .pca_analyzer .project_new_data (new_data )


            ax =self .pca_figure .gca ()
            ax .scatter (projected_data [0 ,0 ],projected_data [0 ,1 ],c ='red',s =100 ,marker ='*',label ='New Point')
            ax .legend ()
            self .pca_canvas .draw ()


            new_point_info ="New Point Projection:\n"
            for i ,coord in enumerate (projected_data [0 ]):
                new_point_info +=f"PC{i +1 }: {coord :.3f}\n"
            self .pca_results_text .append (new_point_info )

    def update_pca_and_corr_matrix_initial (self ):
        if self .data is None :
            return 

        self .update_pca ()
        self .update_corr_matrix ()

    def create_time_series_tab (self ):

        main_layout =QVBoxLayout (self .time_series_tab )


        plots_splitter =QSplitter (Qt .Orientation .Horizontal )


        stacked_kde_container =QWidget ()
        stacked_kde_layout =QVBoxLayout (stacked_kde_container )


        self .stacked_kde_figure =Figure ()
        self .stacked_kde_canvas =FigureCanvas (self .stacked_kde_figure )


        stacked_kde_toolbar =NavigationToolbar (self .stacked_kde_canvas ,self )


        stacked_kde_layout .addWidget (self .stacked_kde_canvas )
        stacked_kde_layout .addWidget (stacked_kde_toolbar )


        plots_splitter .addWidget (stacked_kde_container )


        line_plot_container =QWidget ()
        line_plot_layout =QVBoxLayout (line_plot_container )


        self .line_plot_figure =Figure ()
        self .line_plot_canvas =FigureCanvas (self .line_plot_figure )


        line_plot_toolbar =NavigationToolbar (self .line_plot_canvas ,self )


        line_plot_layout .addWidget (self .line_plot_canvas )
        line_plot_layout .addWidget (line_plot_toolbar )


        plots_splitter .addWidget (line_plot_container )


        main_layout .addWidget (plots_splitter )

    def calculate_kmo_test (self ,data ):
        with warnings .catch_warnings (record =True )as w :
            warnings .simplefilter ("always")
            try :
                kmo_all ,kmo_model =calculate_kmo (data )
                if len (w )>0 and issubclass (w [-1 ].category ,UserWarning ):
                    print ("Warning: KMO test used Moore-Penrose inverse. Results may be less reliable.")
                return kmo_model 
            except Exception as e :
                print (f"KMO calculation failed: {str (e )}")
                return None 















































































































































    def update_time_series (self ):
        if not self .enable_time_series_checkbox .isChecked ()or self .data is None :
            return 

        try :

            self .stacked_kde_figure .clear ()
            self .line_plot_figure .clear ()


            ax_kde =self .stacked_kde_figure .add_subplot (111 )
            ax_line =self .line_plot_figure .add_subplot (111 )


            time_difference_seconds =self .time_diff_spin_box .value ()*60 


            if self .dI_plot_button .isChecked ():
                data_index =0 if self .delta_I_button .isChecked ()else 2 
                y_label ='ΔI (pA)'if self .delta_I_button .isChecked ()else 'ΔI(fwhm) (pA)'
            else :
                data_index =4 if self .delta_t_button .isChecked ()else 1 
                y_label ='Δt (ms)'if self .delta_t_button .isChecked ()else 'Δt(fwhm) (ms)'


            plot_data =self .data [:,data_index ]*1e3 
            event_times =self .data [:,8 ]


            max_time =np .max (event_times )
            num_bins =int (np .ceil (max_time /time_difference_seconds ))
            time_bins =np .linspace (0 ,num_bins *time_difference_seconds ,num_bins +1 )


            peak_values =[]
            times =[]
            fit_results =[]


            selected_cmap =plt .get_cmap (self .colormap_combo_box .currentText ())


            if self .log_scale_time_series_checkbox .isChecked ():
                plot_data =np .log (plot_data )
                y_label =f'log({y_label })'

            overall_min =np .min (plot_data )
            overall_max =np .max (plot_data )
            x_plot =np .linspace (overall_min ,overall_max ,self .big_plot_bins .value ())

            stack_height =1.0 
            y_offset =0 


            global_fit_result =self .perform_global_fitting (plot_data ,event_times ,time_bins )


            for i ,(start ,end )in enumerate (zip (time_bins [:-1 ],time_bins [1 :])):
                mask =(event_times >=start )&(event_times <end )
                bin_data =plot_data [mask ]

                if len (bin_data )==0 :
                    continue 

                color =selected_cmap (i /(num_bins -1 ))

                if self .kde_button .isChecked ():

                    kde =gaussian_kde (bin_data )
                    y_plot =kde (x_plot )
                    y_plot_normalized =y_plot /np .max (y_plot )*stack_height 
                    ax_kde .fill_between (x_plot ,y_offset ,y_plot_normalized +y_offset ,color =color ,alpha =0.7 )
                    ax_kde .plot (x_plot ,y_plot_normalized +y_offset ,color ='black',linewidth =0.5 )
                else :

                    hist ,bin_edges =np .histogram (bin_data ,bins =self .big_plot_bins .value (),density =True )
                    bin_centers =(bin_edges [:-1 ]+bin_edges [1 :])/2 
                    y_plot_normalized =hist /np .max (hist )*stack_height 
                    ax_kde .bar (bin_centers ,y_plot_normalized ,bottom =y_offset ,width =np .diff (bin_edges ),
                    align ='center',color =color ,alpha =0.7 ,edgecolor ='none')


                peak_index =np .argmax (y_plot_normalized )
                peak_value =x_plot [peak_index ]if self .kde_button .isChecked ()else bin_centers [peak_index ]
                peak_values .append (peak_value )
                times .append ((start +end )/2 /60 )


                if self .show_fit_checkbox .isChecked ():
                    fit_result =self .perform_constrained_time_bin_fitting (bin_data ,x_plot ,global_fit_result ,i )
                    fit_results .append (fit_result )

                    if fit_result is not None :

                        max_fit =np .max (fit_result ['overall_fit'])
                        normalized_components =[comp /max_fit *stack_height for comp in fit_result ['components']]
                        normalized_overall_fit =fit_result ['overall_fit']/max_fit *stack_height 


                        for component in normalized_components :
                            ax_kde .plot (x_plot ,component +y_offset ,'--',color ='black',alpha =0.5 )


                        ax_kde .plot (x_plot ,normalized_overall_fit +y_offset ,'r-',linewidth =2 )


                ax_kde .text (overall_max ,y_offset +stack_height /2 ,f'{start /60 :.1f} min',
                ha ='left',va ='center',fontsize =8 )


                y_offset +=stack_height *1.1 


            ax_kde .set_yticks ([])
            ax_kde .set_xlabel (y_label )
            ax_kde .set_ylabel ('Time')
            ax_kde .set_ylim (0 ,y_offset )
            ax_kde .set_xlim (overall_min ,overall_max )


            sm =plt .cm .ScalarMappable (cmap =selected_cmap ,norm =plt .Normalize (vmin =0 ,vmax =max_time /60 ))
            cbar =self .stacked_kde_figure .colorbar (sm ,ax =ax_kde )
            cbar .set_label ('Time (min)')


            ax_line .plot (times ,peak_values ,marker ='o',linestyle ='-',color ='royalblue')
            ax_line .set_xlabel ('Time (min)')
            ax_line .set_ylabel (f'Peak {y_label }')
            ax_line .grid (True ,which ='both',linestyle ='--',linewidth =0.5 )


            self .stacked_kde_canvas .draw ()
            self .line_plot_canvas .draw ()


            self .fit_results_tab .update_time_series_fit_results (fit_results ,times )

        except Exception as e :
            print (f"Error in update_time_series: {str (e )}")
            traceback .print_exc ()

    def perform_global_fitting (self ,plot_data ,event_times ,time_bins ):
        fitting_type =self .fitting_type_combo .currentText ()

        try :

            hist ,bin_edges =np .histogram (plot_data ,bins =self .big_plot_bins .value (),density =True )
            bin_centers =(bin_edges [:-1 ]+bin_edges [1 :])/2 

            if self .fitting_method_combo .currentText ()=='Automatic':
                n_components =self .determine_components_auto (plot_data )
            else :
                n_components =self .components_spin_box .value ()


            if hasattr (self ,'main_graph_fit_params'):
                initial_params =self .main_graph_fit_params 
            else :
                initial_params =None 


            result =self .fit_model (bin_centers ,hist ,fitting_type ,n_components ,user_params =initial_params )

            return result 

        except Exception as e :
            print (f"Error in perform_global_fitting: {str (e )}")
            traceback .print_exc ()
            return None 

    def create_constrained_params (self ,global_fit_result ,bin_index ):
        constrained_params =Parameters ()

        for param_name ,param in global_fit_result .params .items ():
            try :

                new_param =constrained_params .add (param_name ,value =param .value ,min =param .min ,max =param .max )


                if new_param is None :
                    new_param =constrained_params [param_name ]


                if 'center'in param_name :
                    new_param .set (vary =True ,min =param .value -param .stderr *2 if param .stderr is not None else param .min ,
                    max =param .value +param .stderr *2 if param .stderr is not None else param .max )
                elif 'sigma'in param_name :
                    new_param .set (vary =True ,min =max (param .value *0.5 ,0 ),max =param .value *2 )
                elif 'amplitude'in param_name :
                    new_param .set (vary =True ,min =0 ,max =param .value *5 )
                else :
                    new_param .set (vary =True )

            except Exception as e :
                print (f"Error setting constraint for parameter {param_name }: {str (e )}")

                constrained_params .add (param_name ,value =param .value ,vary =True )

        return constrained_params 

    def perform_constrained_time_bin_fitting (self ,bin_data ,x_plot ,global_fit_result ,bin_index ):
        fitting_type =self .fitting_type_combo .currentText ()

        try :
            if len (bin_data )<3 :
                print ("Not enough data points for fitting")
                return None 


            hist ,bin_edges =np .histogram (bin_data ,bins =self .big_plot_bins .value (),density =True )
            bin_centers =(bin_edges [:-1 ]+bin_edges [1 :])/2 


            constrained_params =self .create_constrained_params (global_fit_result ,bin_index )

            if constrained_params is None or len (constrained_params )==0 :
                print (f"Failed to create constrained parameters for bin {bin_index }")
                return None 


            result =self .fit_model (bin_centers ,hist ,fitting_type ,len (constrained_params )//3 ,user_params =constrained_params )

            if result is None :
                print (f"Fitting failed for bin {bin_index }")
                return None 


            components =result .eval_components (x =x_plot )
            overall_fit =result .eval (x =x_plot )

            return {
            'result':result ,
            'components':list (components .values ()),
            'overall_fit':overall_fit ,
            'n_components':len (constrained_params )//3 ,
            'x_plot':x_plot 
            }
        except Exception as e :
            print (f"Error in perform_constrained_time_bin_fitting for bin {bin_index }: {str (e )}")
            traceback .print_exc ()
            return None 



    def perform_time_series_fitting (self ,data ,x_plot ,y_plot ):
        fitting_type =self .fitting_type_combo .currentText ()

        try :
            if len (data )<3 :
                print ("Not enough data points for fitting")
                return None 


            hist ,bin_edges =np .histogram (data ,bins =self .big_plot_bins .value (),density =True )
            bin_centers =(bin_edges [:-1 ]+bin_edges [1 :])/2 

            if self .fitting_method_combo .currentText ()=='Automatic':
                n_components =self .determine_components_auto (data )
            else :
                n_components =self .components_spin_box .value ()

            print (f"Fitting with {n_components } components")

            if hasattr (self ,'main_graph_fit_params'):
                initial_params =self .main_graph_fit_params 
            else :
                initial_params =None 


            result =self .fit_model (bin_centers ,hist ,fitting_type ,n_components ,user_params =initial_params )
            if result is None :
                return None 


            components =result .eval_components (x =x_plot )
            overall_fit =result .eval (x =x_plot )

            return {
            'result':result ,
            'components':list (components .values ()),
            'overall_fit':overall_fit ,
            'n_components':n_components ,
            'x_plot':x_plot 
            }
        except Exception as e :
            print (f"Error in perform_time_series_fitting: {str (e )}")
            traceback .print_exc ()
            return None 

    def determine_components_auto (self ,data ,threshold =0.05 ,max_components =5 ):

        kde =gaussian_kde (data )
        x_range =np .linspace (min (data ),max (data ),1000 )
        y =kde (x_range )


        peaks ,_ =find_peaks (y ,height =max (y )*threshold ,distance =20 )


        n_components =min (len (peaks ),max_components )


        return max (1 ,n_components )



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
    window =MainApp ()
    window .show ()
    sys .exit (app .exec ())
