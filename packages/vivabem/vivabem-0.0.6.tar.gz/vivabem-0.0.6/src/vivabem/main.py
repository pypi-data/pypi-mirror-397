import glob
import os
import torch
import numpy as np
import pandas as pd


class Imu(object):
    def __init__(self, path, x_col, y_col, z_col, source, sensor=None, freq=None):
        self.path = path
        df = pd.read_csv(self.path)

        # drop last row if it's not complete
        lines = open(self.path, 'r').readlines()
        if (len(lines[0].split(',')) != len(lines[-1].split(','))):
            df.drop(df.tail(1).index, inplace=True)

        # BUG with dtype
        #self.x = torch.tensor(df[x_col])
        #self.y = torch.tensor(df[y_col])
        #self.z = torch.tensor(df[z_col])
        self.x = torch.from_numpy(np.array(df[x_col], dtype=float))
        self.y = torch.from_numpy(np.array(df[y_col], dtype=float))
        self.z = torch.from_numpy(np.array(df[z_col], dtype=float))

        timestamp = 'Timestamp' if source == 'VivaSensing' else 'Timestamp_Sensor(us)'
        self.t = torch.tensor(df[timestamp])
        self.res = torch.sqrt(self.x**2 + self.y**2 + self.z**2)
        self.type = sensor if sensor is not None else None
        self.freq = freq if freq is not None else None

    def __len__(self):
        return len(self.x)

    def __str__(self):
        return f'path: "{self.path}"\nSensor: {self.type}\nFreq: {self.freq} Hz\nDuration: {len(self)/freq} s'


class Hrm(object):
    def __init__(self, path, col, sensor=None, freq=None, offset=0):
        self.path = path
        df = pd.read_csv(self.path)
        #------------------------------
        if (sensor == 'Hr'):
            timestamp = 'Timestamp'

            # check version of SDK
            if ('SdkHR_SGW' in df.columns):
                # previous version
                status = 'Status'
                col = 'SdkHR_SGW'
                #ibi = 'IBI_SGW'
            elif ('SdkHR(bpm)' in df.columns):
                # newer version
                status = 'StatusHR'
                col = 'SdkHR(bpm)'
                #ibi = 'IBI(ms)'
            else:
                print(f'Error: SDK version not supported for heart rate sensor "{sensor}" of path {path}.')

            # drop rows where 'Status' == {0,-99}
            df = df[df[status] != -99]
            df = df[df[status] != 0]
        #------------------------------
        elif (sensor == 'GHr'):
            timestamp = 'Timestamp'
        #------------------------------
        elif (sensor == 'Polar'):
            timestamp = 'timestamp'
        #------------------------------
        else:
            print(f'Error: Heart rate sensor "{sensor}" of {self.id} from moment {self.moment} invalid.')
        #------------------------------
        self.t = torch.tensor(df[timestamp]) + offset
        self.data = torch.tensor(df[col])
        self.type = sensor if sensor is not None else None
        self.freq = freq if freq is not None else None

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return f'path: "{self.path}"\nSensor: {self.type}\nFreq: {self.freq} Hz\nDuration: {len(self)/freq} s'


class PolarAcc(object):
    def __init__(self, path):
        self.path = path
        df = pd.read_csv(self.path)
        self.x = torch.tensor(df['AccX'])
        self.y = torch.tensor(df['AccY'])
        self.z = torch.tensor(df['AccZ'])
        self.t = torch.tensor(df['timestamp'])
        self.tp = torch.tensor(df['POLAR_timestamp'])
        self.type = 'Polar'
        self.freq = 100

    def __len__(self):
        return len(self.x)

    def __str__(self):
        return f'path: "{self.path}"\nSensor: {self.type}\nFreq: {self.freq} Hz\nDuration: {len(self)/freq} s'


class VivaBem(object):
    def __init__(self, file_path, hrm=True, polar=True, acc=None):
        self.dataset_path = '/'.join(file_path.split('/')[:-1])
        self.filename = file_path.split('/')[-1]
        parts = self.filename.split('_')
        self.path = file_path

        #------------------------------
        # common attributes
        #------------------------------
        self.id = parts[0][1:]
        self.protocol = parts[1]
        self.source = 'VivaSensing' if 'VivaSensing' in parts[2] else 'COLA'
        self.arm = parts[3]
        self.dominance = parts[4]
        self.moment = parts[5]
        self.date = '-'.join([parts[6][:4], parts[6][4:6], parts[6][6:8]])
        self.time = parts[7][:2] + 'h' +  parts[7][2:4] + 'm' + parts[7][4:6] + 's'
        self.timestamp = parts[6] + '_' + parts[7].replace('.csv', '')

        #==============================
        # read VivaSensing sensors
        #==============================
        if (self.source == 'VivaSensing'):
            # common regex of files
            prefix = '_'.join([('S' + self.id), self.protocol, 'VivaSensing-'])
            suffix = '_'.join(['', self.arm, self.dominance, self.moment]) + '*.csv'

            # regex for data from sensors
            pattern_acc  = prefix + 'Acc'  + suffix    # Accelerometer data from Samsung SDK
            pattern_lacc = prefix + 'LAcc' + suffix    # Accelerometer data from Google API disregarding gravity
            pattern_gacc = prefix + 'GAcc' + suffix    # Accelerometer data from Google API with the gravity
            pattern_gyro = prefix + 'Gyro' + suffix    # Gyroscope data
            pattern_hrs  = prefix + 'HR'   + suffix    # Heart rate data from Samsung SDK
            pattern_hrg  = prefix + 'GHR'  + suffix    # Heart rate data from Google API
            pattern_hrp  = prefix + 'PolarHr' + suffix # Heart rate data from Polar
            pattern_pacc = prefix + 'PolarAcc' + suffix # Accelerometer data from Polar

            # path or regex"ed" files
            path_lacc = glob.glob(os.path.join(self.dataset_path, pattern_lacc))
            path_gacc = glob.glob(os.path.join(self.dataset_path, pattern_gacc))
            path_acc  = glob.glob(os.path.join(self.dataset_path, pattern_acc))
            path_gyro = glob.glob(os.path.join(self.dataset_path, pattern_gyro))
            path_hrs  = glob.glob(os.path.join(self.dataset_path, pattern_hrs))
            path_hrg  = glob.glob(os.path.join(self.dataset_path, pattern_hrg))
            path_hrp  = glob.glob(os.path.join(self.dataset_path, pattern_hrp))
            path_pacc = glob.glob(os.path.join(self.dataset_path, pattern_pacc))

            #------------------------------
            # accelerometer:
            #------------------------------
            # try to read data in the following order:
            #   - GAcc: data from Google API considering the gravity
            #   - LAcc: data from Google API disregarding gravity
            #   - Acc: data from Samsung SDK
            if (acc == None):
                if (len(path_gacc) == 1):
                    self.acc = Imu(path_gacc[0], 'GaccX(m/s^2)', 'GaccY(m/s^2)', 'GaccZ(m/s^2)', self.source, sensor='GAcc', freq=100)
                elif (len(path_lacc) == 1):
                    self.acc = Imu(path_lacc[0], 'GlaccX(m/s^2)', 'GlaccY(m/s^2)', 'GlaccZ(m/s^2)', self.source, sensor='LAcc', freq=100)
                    print(f'Warning: Accelerometer data form LAcc for {self.filename}.')
                elif (len(path_acc) == 1):
                    self.acc = Imu(path_acc[0], 'AccX(m/s^2)', 'AccY(m/s^2)', 'AccZ(m/s^2)', self.source, sensor='Acc', freq=25)
                    print(f'Warning: Accelerometer data form Acc for {self.filename}.')
                else:
                    #raise Exception('Can\'t read accelerometer data.')
                    print(f'Error (S{self.id}_{self.protocol}_VivaSensing-XAcc_{self.arm}_{self.dominance}_{self.moment}): Can\'t read accelerometer data.')
            #------------------------------
            # GAcc: data from Google API considering the gravity
            elif (acc == 'GAcc'):
                if (len(path_gacc) == 1):
                    self.acc = Imu(path_gacc[0], 'GaccX(m/s^2)', 'GaccY(m/s^2)', 'GaccZ(m/s^2)', self.source, sensor='GAcc', freq=100)
                else:
                    print(f'Error (S{self.id}_{self.protocol}_VivaSensing-GAcc_{self.arm}_{self.dominance}_{self.moment}): Can\'t read accelerometer data.')
                    raise Exception('Can\'t read GAcc accelerometer data.')
            #------------------------------
            # LAcc: data from Google API disregarding gravity
            elif (acc == 'LAcc'):
                if (len(path_lacc) == 1):
                    self.acc = Imu(path_lacc[0], 'GlaccX(m/s^2)', 'GlaccY(m/s^2)', 'GlaccZ(m/s^2)', self.source, sensor='LAcc', freq=100)
                else:
                    print(f'Error (S{self.id}_{self.protocol}_VivaSensing-LAcc_{self.arm}_{self.dominance}_{self.moment}): Can\'t read accelerometer data.')
                    raise Exception('Can\'t read LAcc accelerometer data.')
            #------------------------------
            # Acc: data from Samsung SDK
            elif (acc == 'Acc'):
                if (len(path_acc) == 1):
                    self.acc = Imu(path_acc[0], 'AccX(m/s^2)', 'AccY(m/s^2)', 'AccZ(m/s^2)', self.source, sensor='Acc', freq=25)
                else:
                    print(f'Error (S{self.id}_{self.protocol}_VivaSensing-Acc_{self.arm}_{self.dominance}_{self.moment}): Can\'t read accelerometer data.')
                    raise Exception('Can\'t read Acc accelerometer data.')
            #------------------------------
            else:
                raise Exception(f'Accelerometer option does not exist: {acc}.')

            #------------------------------
            # gyroscope
            #------------------------------
            try:
                self.gyro = Imu(path_gyro[0], 'GyroX(rad/s)', 'GyroY(rad/s)', 'GyroZ(rad/s)', self.source, freq=100)
            except:
                #raise Exception('Can\'t read gyroscope data.')
                self.gyro = None
                print(f'Error (S{self.id}_{self.protocol}_VivaSensing-Gyro_{self.arm}_{self.dominance}_{self.moment}): Can\'t read gyroscope data.')

            #------------------------------
            # HRM
            #------------------------------
            # try to read data in the following order:
            #   - GHR: data from Google API disregarding gravity
            #   - HR: data from Google API considering the gravity
            if hrm:
                try:
                    self.hrp = Hrm(path_hrp[0], 'HR', sensor='Polar', freq=1, offset=3*60*60*1000)
                except:
                    #raise Exception('Can\'t read Polar HR data.')
                    print(f'Error (S{self.id}_{self.protocol}_VivaSensing-PolarHr_{self.arm}_{self.dominance}_{self.moment}): Can\'t read Polar HR data.')

                if (len(path_hrg) == 1):
                    self.hr = Hrm(path_hrg[0], 'GHR_SGW', sensor='GHr', freq=1)
                elif (len(path_hrs) == 1):
                    self.hr = Hrm(path_hrs[0], 'SdkHR_SGW', sensor='Hr', freq=1)
                    print('Warning: HR data from SdkHR.')
                else:
                    #raise Exception('Can\'t read heart rate data.')
                    print(f'Error: Can\'t read heart rate data of {self.id} from moment {self.moment}.')

            #------------------------------
            # Polar accelerometer
            #------------------------------
            if polar:
                try:
                    self.pacc = PolarAcc(path_pacc[0])
                except:
                    #raise Exception('Can\'t read Polar accelerometer data.')
                    print(f'Error (S{self.id}_{self.protocol}_VivaSensing-PolarAcc_{self.arm}_{self.dominance}_{self.moment}): Can\'t read Polar accelerometer data.')

        #==============================
        # read COLA sensors
        #==============================
        else:
            # common regex of files
            prefix = 'S' + self.id + '_' + self.protocol
            suffix = self.arm + '_' + self.dominance + '_' + self.moment + '_*.csv'

            # regex for data from sensors
            regex_imu  = prefix + '_COLA_'     + suffix  # Acc, Gyro, HRM (fusion)
            regex_hrm  = prefix + '_COLA-HRM_' + suffix  # HRM COLA
            regex_hrp  = prefix + '_POLAR_'    + suffix  # HRm Polar

            # path or regex"ed" files
            path_imu = glob.glob(os.path.join(self.dataset_path, regex_imu))
            path_hrm = glob.glob(os.path.join(self.dataset_path, regex_hrm))
            path_hrp = glob.glob(os.path.join(self.dataset_path, regex_hrp))

            #------------------------------
            # accelerometer, gyroscope
            #------------------------------
            self.acc  = Imu(path_imu[0], 'ACC_X(m/s^2)', 'ACC_Y', 'ACC_Z', self.source, freq=100)
            self.gyro = Imu(path_imu[0], 'GYR_X(degree/sec)', 'GYR_Y', 'GYR_Z', self.source, freq=100)

            #------------------------------
            # HRM
            #------------------------------
            if hrm:
                try:
                    self.hrmf = Hrm(path_imu[0], 'HR(bpm)', freq=100)  # COLA (fusion)
                    self.hrm  = Hrm(path_hrm[0], ' bpm', freq=1)       # COLA-HRM
                except:
                    #raise Exception('Can\'t read heart rate data.')
                    print(f'Error (S{self.id}_{self.protocol}_COLA-HRM_{self.arm}_{self.dominance}_{self.moment}): Can\'t read HRM data.')

            #------------------------------
            # Polar
            #------------------------------
            if polar:
                try:
                    self.hrp  = Hrm(path_hrp[0], ' HR', freq=1)         # POLAR
                except:
                    #raise Exception('Can\'t read Polar HR data.')
                    print(f'Error (S{self.id}_{self.protocol}_POLAR_{self.arm}_{self.dominance}_{self.moment}): Can\'t read Polar HR data.')

    def __len__(self):
        return len(self.acc.x)

    def __repr__(self):
        return f'S{self.id}_{self.source}_{self.arm}_{self.dominance}_{self.moment}'

    def __str__(self):
        return f'Subject ID: {self.id}\nProtocol: {self.protocol}\nArm: {self.arm}\nMoment: {self.moment}'
