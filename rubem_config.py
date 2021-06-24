# coding=utf-8
        
defaultConfigSchema = {
        'SIM_TIME': {
                    'start' : '01/01/2000',
                    'end' : '01/02/2000'
        },
        'FILES': { 
                'input' : '',
                'output' : '',
                'dem' : '',
                'demtif' : '',
                'clone' : '',
                'etp' : '',
                'prec' : '',
                'ndvi' : '',
                'ndvimax' : '', 
                'ndvimin' : '',                 
                'kp' : '',
                'landuse' : '',
                'solo' : '',
                'samples' : '',
                'etpFilePrefix' : '',
                'precFilePrefix' : '',
                'ndviFilePrefix' : '',  
                'kpFilePrefix' : '',
                'landuseFilePrefix' : ''
        },
        'PARAMETERS': {
                'rainydays' : '',
                'a_i' : '',
                'a_o' : '',
                'a_s' : '',
                'a_v' : '',
                'manning' : '',
                'dg' : '',
                'kr' : '',
                'capCampo' : '',
                'porosidade' : '',
                'saturacao' : '',
                'pontomurcha' : '',
                'zr' : '',
                'kcmin' : '',
                'kcmax' : ''
        },
        'GRID': {
                'grid' : '500.00'
        },
        'CALIBRATION': {
                'alfa' : '4.500',
                'b' : '0.500',
                'w1' : '0.333',
                'w2' : '0.333',
                'w3' : '0.334',
                'rcd' : '5.000',
                'f' : '0.500',
                'alfa_gw' : '0.500',
                'x' : '0.500'
        },
        'INITIAL SOIL CONDITIONS': {
                'ftur_ini' : '1.000',
                'eb_ini' : '0.100',
                'eb_lim' : '1.000',
                'tus_ini' : '1.000'
        },
        'CONSTANT': {
                'fpar_max' : '0.950',
                'fpar_min' : '0.001',
                'lai_max' : '12.000',
                'i_imp' : '2.500'
        },
        'GENERATE_FILE': {
                'Int' : 'True', 
                'Eb' : 'False',
                'Esd' : 'False',
                'Evp' : 'False',
                'Lf' : 'False',
                'Rec' : 'False', 
                'Tur' : 'False', 
                'Vazao' : 'False',
                'auxQtot' : 'False', 
                'auxRec' : 'False',
                'genTss': 'False'
        }
}
        
maxValuesDic = {
        'GRID': {
                'grid' : '500.00'
        },
        'CALIBRATION': {
                'alfa' : '4.500',
                'b' : '0.500',
                'w1' : '0.333',
                'w2' : '0.333',
                'w3' : '0.334',
                'rcd' : '5.000',
                'f' : '0.500',
                'alfa_gw' : '0.500',
                'x' : '0.500'
        },
        'INITIAL SOIL CONDITIONS': {
                'ftur_ini' : '1.000',
                'eb_ini' : '0.100',
                'eb_lim' : '1.000',
                'tus_ini' : '1.000'
        },
        'CONSTANT': {
                'fpar_max' : '0.950',
                'fpar_min' : '0.001',
                'lai_max' : '12.000',
                'i_imp' : '2.500'
        }
}

minValuesDic = {
        'GRID': {
                'grid' : '500.00'
        },
        'CALIBRATION': {
                'alfa' : '4.500',
                'b' : '0.500',
                'w1' : '0.333',
                'w2' : '0.333',
                'w3' : '0.334',
                'rcd' : '5.000',
                'f' : '0.500',
                'alfa_gw' : '0.500',
                'x' : '0.500'
        },
        'INITIAL SOIL CONDITIONS': {
                'ftur_ini' : '1.000',
                'eb_ini' : '0.100',
                'eb_lim' : '1.000',
                'tus_ini' : '1.000'
        },
        'CONSTANT': {
                'fpar_max' : '0.950',
                'fpar_min' : '0.001',
                'lai_max' : '12.000',
                'i_imp' : '2.500'
        }
}