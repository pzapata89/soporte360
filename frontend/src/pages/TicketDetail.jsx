import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getTicket, getComments, createComment, getHistory, updateTicketStatus, assignTicket, getUsers, getCategories } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, MessageSquare, History, Send, CheckCircle, User } from 'lucide-react';

const TicketDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [ticket, setTicket] = useState(null);
  const [comments, setComments] = useState([]);
  const [history, setHistory] = useState([]);
  const [users, setUsers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('comments');

  const userRole = (user?.role || user?.rol || '').toLowerCase();
  const isAdmin = userRole === 'admin';
  const isSupervisor = userRole === 'supervisor';
  const isTecnico = userRole === 'tecnico';
  const isUsuario = userRole === 'usuario';

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch main ticket data first
      const [ticketRes, commentsRes, historyRes, categoriesRes] = await Promise.all([
        getTicket(id),
        getComments(id),
        getHistory(id),
        getCategories()
      ]);
      
      // Try to get users, but don't fail if 403 (user doesn't have permission)
      let usersData = [];
      try {
        const usersRes = await getUsers();
        usersData = usersRes.data || [];
      } catch (userErr) {
        // If 403, user doesn't have permission to see users list
        if (userErr.response?.status === 403) {
          console.log('User does not have permission to view users list');
          usersData = [];
        } else {
          throw userErr; // Re-throw other errors
        }
      }
      
      setTicket(ticketRes.data);
      setComments(commentsRes.data || []);
      setHistory(historyRes.data || []);
      setUsers(usersData);
      setCategories(categoriesRes.data || []);
    } catch (err) {
      setError('Error al cargar el ticket');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await updateTicketStatus(id, newStatus);
      fetchData();
    } catch (err) {
      setError('Error al actualizar el estado');
    }
  };

  const handleAssign = async (userId) => {
    try {
      await assignTicket(id, userId || null);
      fetchData();
    } catch (err) {
      setError('Error al asignar el ticket');
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setSubmitting(true);
      await createComment(id, { comment: newComment });
      setNewComment('');
      fetchData();
    } catch (err) {
      setError('Error al agregar comentario');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800',
      on_hold: 'bg-orange-100 text-orange-800',
      closed: 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status) => {
    const labels = {
      open: 'Abierto',
      in_progress: 'En Progreso',
      on_hold: 'En Espera',
      closed: 'Cerrado'
    };
    return labels[status] || status;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-blue-100 text-blue-800',
      high: 'bg-orange-100 text-orange-800',
      urgent: 'bg-red-100 text-red-800'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityLabel = (priority) => {
    const labels = {
      low: 'Baja',
      medium: 'Media',
      high: 'Alta',
      urgent: 'Urgente'
    };
    return labels[priority] || priority;
  };

  const getActionLabel = (action) => {
    const labels = {
      CREATION: 'Creación',
      STATUS_CHANGE: 'Cambio de Estado',
      ASSIGNMENT: 'Asignación',
      COMMENT: 'Comentario'
    };
    return labels[action] || action;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('es-ES');
  };

  const getCategoryName = (id) => {
    const cat = categories.find(c => c.id === id);
    return cat?.name || cat?.nombre || 'Sin categoría';
  };

  const getUserName = (id) => {
    const u = users.find(u => u.id === id);
    return u?.full_name || u?.nombre || u?.email || 'Usuario #' + id;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Ticket no encontrado</p>
        <Link to="/tickets" className="text-blue-600 hover:underline mt-4 inline-block">
          Volver a tickets
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/tickets')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft size={24} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {ticket.ticket_code}
          </h1>
          <p className="text-gray-500">{ticket.title || ticket.titulo}</p>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Details Card */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Detalles del Ticket</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-500">Estado</label>
                <div className="mt-1">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(ticket.status || ticket.estado)}`}>
                    {getStatusLabel(ticket.status || ticket.estado)}
                  </span>
                </div>
              </div>
              <div>
                <label className="text-sm text-gray-500">Prioridad</label>
                <div className="mt-1">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(ticket.priority || ticket.prioridad)}`}>
                    {getPriorityLabel(ticket.priority || ticket.prioridad)}
                  </span>
                </div>
              </div>
              <div>
                <label className="text-sm text-gray-500">Categoría</label>
                <p className="mt-1 font-medium">{getCategoryName(ticket.category_id || ticket.categoria_id)}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Creado por</label>
                <p className="mt-1 font-medium">{getUserName(ticket.created_by || ticket.creado_por)}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Asignado a</label>
                <p className="mt-1 font-medium">
                  {ticket.assigned_to || ticket.asignado_a ? getUserName(ticket.assigned_to || ticket.asignado_a) : 'Sin asignar'}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Fecha de creación</label>
                <p className="mt-1 font-medium">{formatDate(ticket.created_at)}</p>
              </div>
            </div>
            <div className="mt-6">
              <label className="text-sm text-gray-500">Descripción</label>
              <p className="mt-1 text-gray-700 whitespace-pre-wrap">{ticket.description || ticket.descripcion}</p>
            </div>
          </div>

          {/* Comments & History Tabs */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="border-b border-gray-200">
              <div className="flex">
                <button
                  onClick={() => setActiveTab('comments')}
                  className={`px-6 py-3 text-sm font-medium flex items-center gap-2 ${
                    activeTab === 'comments'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <MessageSquare size={18} />
                  Comentarios ({comments.length})
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-6 py-3 text-sm font-medium flex items-center gap-2 ${
                    activeTab === 'history'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <History size={18} />
                  Historial ({history.length})
                </button>
              </div>
            </div>

            <div className="p-6">
              {activeTab === 'comments' ? (
                <div className="space-y-4">
                  {/* Comment Form */}
                  <form onSubmit={handleCommentSubmit} className="mb-6">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        placeholder="Escribe un comentario..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={submitting}
                      />
                      <button
                        type="submit"
                        disabled={submitting || !newComment.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                      >
                        <Send size={18} />
                      </button>
                    </div>
                  </form>

                  {/* Comments List */}
                  {comments.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No hay comentarios</p>
                  ) : (
                    <div className="space-y-4">
                      {comments.map((comment) => (
                        <div key={comment.id} className="flex gap-3 p-4 bg-gray-50 rounded-lg">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <User size={16} className="text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-sm">
                                {comment.user?.full_name || comment.user?.nombre || 'Usuario'}
                              </span>
                              <span className="text-xs text-gray-500">
                                {formatDate(comment.created_at)}
                              </span>
                            </div>
                            <p className="text-gray-700">{comment.comment || comment.comentario}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {history.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No hay historial</p>
                  ) : (
                    <div className="space-y-4">
                      {history.map((item) => (
                        <div key={item.id} className="flex gap-3 p-4 bg-gray-50 rounded-lg">
                          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <History size={16} className="text-purple-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-sm">
                                {getActionLabel(item.action || item.accion)}
                              </span>
                              <span className="text-xs text-gray-500">
                                {formatDate(item.timestamp || item.created_at)}
                              </span>
                            </div>
                            {item.from_status && item.to_status && (
                              <p className="text-sm text-gray-600">
                                De: {item.from_status} → A: {item.to_status}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar Actions - Usuario */}
        {isUsuario && ticket.created_by === user?.id && (
          <div className="space-y-4">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Acciones</h3>
              <div className="space-y-2">
                {(ticket.status === 'open' || ticket.status === 'in_progress' || ticket.status === 'on_hold') && (
                  <button
                    onClick={() => handleStatusChange('closed')}
                    className="w-full px-4 py-2 rounded-lg text-left text-sm font-medium bg-gray-50 hover:bg-gray-100 text-gray-700 transition-colors"
                  >
                    Cerrar Ticket
                  </button>
                )}
                {ticket.status === 'closed' && (
                  <button
                    onClick={() => handleStatusChange('open')}
                    className="w-full px-4 py-2 rounded-lg text-left text-sm font-medium bg-gray-50 hover:bg-gray-100 text-gray-700 transition-colors"
                  >
                    Reabrir Ticket
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Sidebar Actions */}
        {(isAdmin || isSupervisor || isTecnico) && (
          <div className="space-y-4">
            {/* Status Actions */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Cambiar Estado</h3>
              <div className="space-y-2">
                {['open', 'in_progress', 'on_hold', 'closed'].map((status) => (
                  <button
                    key={status}
                    onClick={() => handleStatusChange(status)}
                    disabled={(ticket.status || ticket.estado) === status}
                    className={`w-full px-4 py-2 rounded-lg text-left text-sm font-medium transition-colors ${
                      (ticket.status || ticket.estado) === status
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    {getStatusLabel(status)}
                  </button>
                ))}
              </div>
            </div>

            {/* Assignment */}
            {(isAdmin || isSupervisor) && (
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="font-semibold text-gray-900 mb-4">Asignar Técnico</h3>
                <select
                  onChange={(e) => handleAssign(e.target.value || null)}
                  value={ticket.assigned_to || ticket.asignado_a || ''}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Sin asignar</option>
                  {users
                    .filter(u => u.role === 'TECNICO' || u.rol === 'TECNICO' || u.role === 'tecnico' || u.rol === 'tecnico')
                    .map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.full_name || user.nombre || user.email}
                      </option>
                    ))}
                </select>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TicketDetail;
