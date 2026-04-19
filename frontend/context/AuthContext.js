import React from 'react';
import { TextInput } from 'react-native';

export default function FormInput(props) {
  return (
    <TextInput
      {...props}
      style={{
        borderWidth: 1,
        borderColor: '#ccc',
        borderRadius: 8,
        padding: 12,
        marginBottom: 12
      }}
    />
  );
}
