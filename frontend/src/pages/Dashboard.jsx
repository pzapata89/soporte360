import React, { useState, useEffect } from 'react';
import { getGeneralReport, getCategoryReport, getTechnicianReport } from '../services/api';
import { Ticket, CheckCircle, Clock, BarChart3 } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const Dashboard = () => {
  const [generalReport, setGeneralReport] = useState(null);
  const [categoryReport, setCategoryReport] = useState([]);
  const [technicianReport, setTechnicianReport] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const [generalRes, categoryRes, technicianRes] = await Promise.all([
        getGeneralReport(),
        getCategoryReport(),
        getTechnicianReport()
      ]);
      setGeneralReport(generalRes.data);
      setCategoryReport(categoryRes.data || []);
      setTechnicianReport(technicianRes.data || []);
    } catch (err) {
      setError('Error al cargar los reportes');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg">
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Tickets</p>
              <p className="text-2xl font-bold text-gray-900">{generalReport?.total_tickets || 0}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Ticket className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Abiertos</p>
              <p className="text-2xl font-bold text-yellow-600">{generalReport?.open_tickets || 0}</p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-full">
              <Clock className="text-yellow-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Cerrados</p>
              <p className="text-2xl font-bold text-green-600">{generalReport?.closed_tickets || 0}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <CheckCircle className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Tiempo Promedio</p>
              <p className="text-2xl font-bold text-purple-600">
                {generalReport?.avg_resolution_time_hours
                  ? `${Math.round(generalReport.avg_resolution_time_hours)}h`
                  : 'N/A'}
              </p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <BarChart3 className="text-purple-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6">
        {/* Tickets by Category */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Tickets por Categoría</h2>
          {categoryReport.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryReport}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="total_tickets"
                  nameKey="category_name"
                >
                  {categoryReport.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No hay datos disponibles
            </div>
          )}
        </div>

        {/* Tickets by Technician */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Tickets por Técnico</h2>
          {technicianReport.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={technicianReport}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="full_name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="total_assigned" fill="#3b82f6" name="Total" />
                <Bar dataKey="closed_tickets" fill="#10b981" name="Cerrados" />
                <Bar dataKey="open_tickets" fill="#f59e0b" name="Abiertos" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No hay datos disponibles
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
