# أمثلة تطبيقات الجوال لنظام نُظم

## React Native Example

### 1. إعداد المصادقة والـ API
```javascript
// services/api.js
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://your-domain.com/api/v1';

class ApiService {
  constructor() {
    this.token = null;
  }

  async getToken() {
    if (!this.token) {
      this.token = await AsyncStorage.getItem('auth_token');
    }
    return this.token;
  }

  async setToken(token) {
    this.token = token;
    await AsyncStorage.setItem('auth_token', token);
  }

  async clearToken() {
    this.token = null;
    await AsyncStorage.removeItem('auth_token');
  }

  async request(endpoint, options = {}) {
    const token = await this.getToken();
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const data = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        await this.clearToken();
        throw new Error('انتهت صلاحية الجلسة');
      }
      throw new Error(data.error || 'خطأ في الخادم');
    }

    return data;
  }

  // تسجيل دخول الموظف
  async employeeLogin(employeeId, nationalId) {
    const data = await this.request('/auth/employee-login', {
      method: 'POST',
      body: JSON.stringify({
        employee_id: employeeId,
        national_id: nationalId,
      }),
    });

    await this.setToken(data.token);
    return data;
  }

  // جلب الملف الشخصي للموظف
  async getEmployeeProfile() {
    return this.request('/employee/profile');
  }

  // تسجيل الحضور
  async checkIn() {
    return this.request('/attendance/check-in', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // تسجيل الانصراف
  async checkOut() {
    return this.request('/attendance/check-out', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // جلب ملخص الحضور
  async getAttendanceSummary() {
    return this.request('/employee/attendance/summary');
  }

  // جلب مركبات الموظف
  async getMyVehicles() {
    const profile = await this.getEmployeeProfile();
    return this.request(`/employees/${profile.id}/vehicles`);
  }

  // جلب رواتب الموظف
  async getMySalaries() {
    const profile = await this.getEmployeeProfile();
    return this.request(`/employees/${profile.id}/salaries`);
  }
}

export default new ApiService();
```

### 2. شاشة تسجيل الدخول
```javascript
// screens/LoginScreen.js
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import ApiService from '../services/api';

const LoginScreen = ({ navigation }) => {
  const [employeeId, setEmployeeId] = useState('');
  const [nationalId, setNationalId] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!employeeId || !nationalId) {
      Alert.alert('خطأ', 'يرجى إدخال رقم الموظف والهوية الوطنية');
      return;
    }

    setLoading(true);
    try {
      const result = await ApiService.employeeLogin(employeeId, nationalId);
      Alert.alert('نجح تسجيل الدخول', `مرحباً ${result.employee.name}`);
      navigation.replace('Dashboard');
    } catch (error) {
      Alert.alert('خطأ في تسجيل الدخول', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>نظام نُظم</Text>
      <Text style={styles.subtitle}>بوابة الموظفين</Text>

      <TextInput
        style={styles.input}
        placeholder="رقم الموظف"
        value={employeeId}
        onChangeText={setEmployeeId}
        textAlign="right"
      />

      <TextInput
        style={styles.input}
        placeholder="رقم الهوية الوطنية"
        value={nationalId}
        onChangeText={setNationalId}
        textAlign="right"
        secureTextEntry
      />

      <TouchableOpacity
        style={styles.button}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>تسجيل الدخول</Text>
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#2c3e50',
  },
  subtitle: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 40,
    color: '#7f8c8d',
  },
  input: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  button: {
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default LoginScreen;
```

### 3. شاشة لوحة التحكم الرئيسية
```javascript
// screens/DashboardScreen.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  RefreshControl,
} from 'react-native';
import ApiService from '../services/api';

const DashboardScreen = ({ navigation }) => {
  const [profile, setProfile] = useState(null);
  const [attendanceSummary, setAttendanceSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [profileData, summaryData] = await Promise.all([
        ApiService.getEmployeeProfile(),
        ApiService.getAttendanceSummary(),
      ]);
      
      setProfile(profileData);
      setAttendanceSummary(summaryData);
    } catch (error) {
      Alert.alert('خطأ', error.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCheckIn = async () => {
    try {
      await ApiService.checkIn();
      Alert.alert('نجح', 'تم تسجيل الحضور بنجاح');
      loadData(); // إعادة تحميل البيانات
    } catch (error) {
      Alert.alert('خطأ', error.message);
    }
  };

  const handleCheckOut = async () => {
    try {
      await ApiService.checkOut();
      Alert.alert('نجح', 'تم تسجيل الانصراف بنجاح');
      loadData(); // إعادة تحميل البيانات
    } catch (error) {
      Alert.alert('خطأ', error.message);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text>جاري التحميل...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* معلومات الموظف */}
      <View style={styles.profileCard}>
        <Text style={styles.welcomeText}>مرحباً، {profile?.name}</Text>
        <Text style={styles.infoText}>رقم الموظف: {profile?.employee_id}</Text>
        <Text style={styles.infoText}>القسم: {profile?.department}</Text>
        <Text style={styles.infoText}>المسمى الوظيفي: {profile?.job_title}</Text>
      </View>

      {/* بطاقة الحضور */}
      <View style={styles.attendanceCard}>
        <Text style={styles.cardTitle}>الحضور اليوم</Text>
        
        <View style={styles.attendanceButtons}>
          <TouchableOpacity
            style={[
              styles.attendanceButton,
              attendanceSummary?.today_status?.checked_in && styles.disabledButton
            ]}
            onPress={handleCheckIn}
            disabled={attendanceSummary?.today_status?.checked_in}
          >
            <Text style={styles.buttonText}>
              {attendanceSummary?.today_status?.checked_in ? 'تم التسجيل' : 'تسجيل الحضور'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.attendanceButton,
              styles.checkOutButton,
              (!attendanceSummary?.today_status?.checked_in || 
               attendanceSummary?.today_status?.checked_out) && styles.disabledButton
            ]}
            onPress={handleCheckOut}
            disabled={!attendanceSummary?.today_status?.checked_in || 
                     attendanceSummary?.today_status?.checked_out}
          >
            <Text style={styles.buttonText}>
              {attendanceSummary?.today_status?.checked_out ? 'تم التسجيل' : 'تسجيل الانصراف'}
            </Text>
          </TouchableOpacity>
        </View>

        {attendanceSummary?.today_status?.check_in_time && (
          <Text style={styles.timeText}>
            وقت الحضور: {new Date(attendanceSummary.today_status.check_in_time).toLocaleTimeString('ar-SA')}
          </Text>
        )}
        
        {attendanceSummary?.today_status?.check_out_time && (
          <Text style={styles.timeText}>
            وقت الانصراف: {new Date(attendanceSummary.today_status.check_out_time).toLocaleTimeString('ar-SA')}
          </Text>
        )}
      </View>

      {/* إحصائيات الشهر */}
      <View style={styles.statsCard}>
        <Text style={styles.cardTitle}>إحصائيات الشهر</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{attendanceSummary?.monthly_summary?.present_days || 0}</Text>
            <Text style={styles.statLabel}>أيام الحضور</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{attendanceSummary?.monthly_summary?.absent_days || 0}</Text>
            <Text style={styles.statLabel}>أيام الغياب</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{attendanceSummary?.monthly_summary?.late_days || 0}</Text>
            <Text style={styles.statLabel}>أيام التأخير</Text>
          </View>
        </View>
      </View>

      {/* أزرار التنقل */}
      <View style={styles.navigationButtons}>
        <TouchableOpacity
          style={styles.navButton}
          onPress={() => navigation.navigate('Vehicles')}
        >
          <Text style={styles.navButtonText}>مركباتي</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navButton}
          onPress={() => navigation.navigate('Salaries')}
        >
          <Text style={styles.navButtonText}>الرواتب</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navButton}
          onPress={() => navigation.navigate('Attendance')}
        >
          <Text style={styles.navButtonText}>سجل الحضور</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 15,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  welcomeText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'right',
    color: '#2c3e50',
  },
  infoText: {
    fontSize: 16,
    marginBottom: 5,
    textAlign: 'right',
    color: '#7f8c8d',
  },
  attendanceCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'right',
    color: '#2c3e50',
  },
  attendanceButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  attendanceButton: {
    backgroundColor: '#27ae60',
    padding: 15,
    borderRadius: 8,
    flex: 0.48,
    alignItems: 'center',
  },
  checkOutButton: {
    backgroundColor: '#e74c3c',
  },
  disabledButton: {
    backgroundColor: '#bdc3c7',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  timeText: {
    fontSize: 14,
    textAlign: 'center',
    color: '#7f8c8d',
    marginBottom: 5,
  },
  statsCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3498db',
  },
  statLabel: {
    fontSize: 14,
    color: '#7f8c8d',
    textAlign: 'center',
  },
  navigationButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  navButton: {
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 8,
    width: '48%',
    alignItems: 'center',
    marginBottom: 10,
  },
  navButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default DashboardScreen;
```

## Flutter Example

### 1. خدمة الـ API
```dart
// services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String _baseUrl = 'https://your-domain.com/api/v1';
  static const String _tokenKey = 'auth_token';

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> setToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  static Future<Map<String, dynamic>> _request(
    String endpoint, {
    String method = 'GET',
    Map<String, dynamic>? body,
    bool requireAuth = true,
  }) async {
    final url = Uri.parse('$_baseUrl$endpoint');
    final headers = {'Content-Type': 'application/json'};

    if (requireAuth) {
      final token = await getToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    http.Response response;

    switch (method.toUpperCase()) {
      case 'POST':
        response = await http.post(url, headers: headers, body: json.encode(body));
        break;
      case 'PUT':
        response = await http.put(url, headers: headers, body: json.encode(body));
        break;
      case 'DELETE':
        response = await http.delete(url, headers: headers);
        break;
      default:
        response = await http.get(url, headers: headers);
    }

    final data = json.decode(response.body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return data;
    } else {
      if (response.statusCode == 401) {
        await clearToken();
        throw Exception('انتهت صلاحية الجلسة');
      }
      throw Exception(data['error'] ?? 'خطأ في الخادم');
    }
  }

  // تسجيل دخول الموظف
  static Future<Map<String, dynamic>> employeeLogin(String employeeId, String nationalId) async {
    final data = await _request(
      '/auth/employee-login',
      method: 'POST',
      body: {
        'employee_id': employeeId,
        'national_id': nationalId,
      },
      requireAuth: false,
    );

    await setToken(data['token']);
    return data;
  }

  // جلب الملف الشخصي
  static Future<Map<String, dynamic>> getEmployeeProfile() async {
    return await _request('/employee/profile');
  }

  // تسجيل الحضور
  static Future<Map<String, dynamic>> checkIn() async {
    return await _request('/attendance/check-in', method: 'POST', body: {});
  }

  // تسجيل الانصراف
  static Future<Map<String, dynamic>> checkOut() async {
    return await _request('/attendance/check-out', method: 'POST', body: {});
  }

  // جلب ملخص الحضور
  static Future<Map<String, dynamic>> getAttendanceSummary() async {
    return await _request('/employee/attendance/summary');
  }

  // جلب مركبات الموظف
  static Future<Map<String, dynamic>> getMyVehicles() async {
    final profile = await getEmployeeProfile();
    return await _request('/employees/${profile['id']}/vehicles');
  }

  // جلب رواتب الموظف
  static Future<Map<String, dynamic>> getMySalaries() async {
    final profile = await getEmployeeProfile();
    return await _request('/employees/${profile['id']}/salaries');
  }
}
```

### 2. شاشة تسجيل الدخول
```dart
// screens/login_screen.dart
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _employeeIdController = TextEditingController();
  final _nationalIdController = TextEditingController();
  bool _isLoading = false;

  Future<void> _handleLogin() async {
    if (_employeeIdController.text.isEmpty || _nationalIdController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('يرجى إدخال رقم الموظف والهوية الوطنية')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final result = await ApiService.employeeLogin(
        _employeeIdController.text,
        _nationalIdController.text,
      );

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('مرحباً ${result['employee']['name']}')),
      );

      Navigator.pushReplacementNamed(context, '/dashboard');
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطأ في تسجيل الدخول: $error')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      body: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'نظام نُظم',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[800],
              ),
            ),
            SizedBox(height: 10),
            Text(
              'بوابة الموظفين',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 40),
            
            TextField(
              controller: _employeeIdController,
              textAlign: TextAlign.right,
              decoration: InputDecoration(
                labelText: 'رقم الموظف',
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            SizedBox(height: 15),
            
            TextField(
              controller: _nationalIdController,
              textAlign: TextAlign.right,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'رقم الهوية الوطنية',
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            SizedBox(height: 20),
            
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _handleLogin,
                child: _isLoading
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text('تسجيل الدخول', style: TextStyle(fontSize: 18)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

## الخلاصة

تم إنشاء API متكامل يدعم:

- **مصادقة آمنة** باستخدام JWT
- **إدارة الموظفين** الكاملة  
- **تسجيل الحضور والانصراف**
- **إدارة المركبات والرواتب**
- **إحصائيات متقدمة**
- **بوابة الموظفين المستقلة**

يمكن استخدام هذا API مع أي تطبيق جوال أو نظام خارجي يدعم HTTP و JSON.