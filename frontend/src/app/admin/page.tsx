'use client';
import { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export default function AdminPage() {
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setError('Нет токена');
      return;
    }

    axios
      .get(`${API_URL}/admin-data`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((res) => {
        setMessage(res.data.message);
      })
      .catch((err) => {
        setError('Нет доступа или ошибка');
        console.error(err);
      });
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Админ-панель</h1>
      {message && <p className="text-green-600">{message}</p>}
      {error && <p className="text-red-600">{error}</p>}
    </div>
  );
}
