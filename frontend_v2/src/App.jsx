import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import AppLayout from "./layouts/AppLayout";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import VerifyLogin from "./pages/VerifyLogin";
import Communities from "./pages/Communities";
import CommunityChat from "./pages/CommunityChat";
import HelpRequests from "./pages/HelpRequests";
import Conversations from "./pages/Conversations";
import ConversationChat from "./pages/ConversationChat";
import Safety from "./pages/Safety";
import Profile from "./pages/Profile";
import Admin from "./pages/Admin";
import ForgotPassword from "./pages/ForgotPassword";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/register" element={<Register />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      <Route path="/verify-login" element={<VerifyLogin />} />

      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/communities" element={<Communities />} />
        <Route path="/communities/:id" element={<CommunityChat />} />
        <Route path="/help" element={<HelpRequests />} />
        <Route path="/messages" element={<Conversations />} />
        <Route path="/messages/:id" element={<ConversationChat />} />
        <Route path="/safety" element={<Safety />} />
        <Route path="/profile" element={<Profile />} />
        {/* Admin pages: only reachable when the backend confirms admin rights */}
        <Route path="/admin" element={<AdminRoute><Admin /></AdminRoute>} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
