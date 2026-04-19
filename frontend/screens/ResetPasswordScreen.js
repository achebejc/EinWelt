import React, { useState } from 'react';
import { View, Button, Alert } from 'react-native';
import axios from 'axios';
import FormInput from '../components/FormInput';

const API_URL = process.env.EXPO_PUBLIC_API_URL;

export default function ResetPasswordScreen() {
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const submit = async () => {
    try {
      await axios.post(`${API_URL}/auth/reset-password`, { token, new_password: newPassword });
      Alert.alert('Success', 'Password reset.');
    } catch (err) {
      Alert.alert('Error', err?.response?.data?.detail || 'Reset failed');
    }
  };

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <FormInput placeholder="Reset token" value={token} onChangeText={setToken} />
      <FormInput placeholder="New password" value={newPassword} onChangeText={setNewPassword} secureTextEntry />
      <Button title="Reset password" onPress={submit} />
    </View>
  );
}
