import React from 'react';
import { View, Text } from 'react-native';

export default function SettingsScreen() {
  return (
    <View style={{ flex: 1, padding: 20, gap: 12 }}>
      <Text style={{ fontSize: 22, fontWeight: '700' }}>Settings</Text>
      <Text>- Accessibility mode toggle</Text>
      <Text>- Language selection</Text>
      <Text>- Privacy controls</Text>
      <Text>- Notification preferences</Text>
    </View>
  );
}
