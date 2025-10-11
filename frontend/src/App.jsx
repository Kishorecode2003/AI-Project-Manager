
import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import { Layout, Menu } from "antd";
import {
  DashboardOutlined,
  ProfileOutlined,
  TeamOutlined,
  SyncOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import Dashboard from "./components/Dashboard";
import Tasks from "./components/Tasks";
import Consultants from "./components/Consultants";
import Updates from "./components/Updates";
import Scheduler from "./components/Scheduler";
import DraftReplyTab from "./components/DraftReplyTab";
import "./styles.css";

const { Header, Sider, Content } = Layout;

function AppLayout() {
  const location = useLocation();
  const selectedKey = location.pathname === "/" ? "dashboard" : location.pathname.slice(1);
  return (
    <Layout style={{ minHeight: "100vh", width: "100vw" }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div className="logo">
          <h2 style={{ color: "white", textAlign: "center", margin: "16px 0" }}>AI PM</h2>
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[selectedKey]}>
          <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
            <Link to="/">Dashboard</Link>
          </Menu.Item>
          <Menu.Item key="tasks" icon={<ProfileOutlined />}>
            <Link to="/tasks">Tasks</Link>
          </Menu.Item>
          <Menu.Item key="consultants" icon={<TeamOutlined />}>
            <Link to="/consultants">Consultants</Link>
          </Menu.Item>
          <Menu.Item key="updates" icon={<SyncOutlined />}>
            <Link to="/updates">Updates</Link>
          </Menu.Item>
          <Menu.Item key="scheduler" icon={<ClockCircleOutlined />}>
            <Link to="/scheduler">Scheduler</Link>
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout style={{ width: "100%" }}>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            fontSize: "18px",
            fontWeight: "bold",
            borderBottom: "1px solid #f0f0f0",
          }}
        >
          AI Project Manager
        </Header>
        <Content
          style={{
            margin: "24px 16px",
            padding: 24,
            background: "#fff",
            borderRadius: 8,
            minHeight: "calc(100vh - 112px)",
            overflow: "auto",
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/consultants" element={<Consultants />} />
            <Route path="/updates" element={<Updates />} />
            <Route path="/scheduler" element={<Scheduler />} />
            <Route path="/draft-reply" element={<DraftReplyTab />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <AppLayout />
    </Router>
  );
}

export default App;
