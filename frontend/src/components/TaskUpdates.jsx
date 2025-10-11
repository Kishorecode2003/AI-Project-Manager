
import React, { useEffect, useState } from "react";
import {
  Card, List, Tag, Typography, Space, Spin, Empty, Tooltip, Divider,
} from "antd";
import {
  ClockCircleOutlined, WarningOutlined, CheckCircleOutlined, SyncOutlined,
  StopOutlined, UserOutlined, CalendarOutlined, ProfileOutlined,
} from "@ant-design/icons";
import api from "../api/api";

const { Text, Title } = Typography;

function TaskUpdates() {
  const [groupedUpdates, setGroupedUpdates] = useState({});
  const [loading, setLoading] = useState(true);

  const getStatusColor = (status) => {
    switch (status) {
      case "Done": return "green";
      case "In Progress": return "blue";
      case "Blocked": return "red";
      case "Not Started": return "default";
      default: return "default";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "Done": return <CheckCircleOutlined />;
      case "In Progress": return <SyncOutlined spin />;
      case "Blocked": return <StopOutlined />;
      case "Not Started": return <ClockCircleOutlined />;
      default: return <ClockCircleOutlined />;
    }
  };

  useEffect(() => {
    const fetchUpdates = async () => {
      try {
        const res = await api.get("/updates/");
        const data = res.data;

        const uniqueUpdates = data.reduce((acc, item) => {
          const key = `${item.task_name}-${item.consultant_email}`;
          if (!acc[key] || new Date(item.created_at) > new Date(acc[key].created_at)) {
            acc[key] = item;
          }
          return acc;
        }, {});

        const groupedByTask = Object.values(uniqueUpdates).reduce((acc, item) => {
          if (!acc[item.task_name]) acc[item.task_name] = [];
          acc[item.task_name].push(item);
          return acc;
        }, {});

        setGroupedUpdates(groupedByTask);
      } catch (err) {
        console.error("Error fetching updates:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchUpdates();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" tip="Loading updates..." />
      </div>
    );
  }

  const taskNames = Object.keys(groupedUpdates);

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        Task Updates Overview
      </Title>
      {taskNames.length === 0 ? (
        <Empty description="No updates available" />
      ) : (
        <List
          grid={{
            gutter: 24, xs: 1, sm: 1, md: 2, lg: 2, xl: 3,
          }}
          dataSource={taskNames}
          renderItem={(taskName) => (
            <List.Item>
              <Card
                title={
                  <Space>
                    <ProfileOutlined />
                    <b>{taskName}</b>
                  </Space>
                }
                bordered={false}
                hoverable
                style={{
                  borderRadius: 12,
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                }}
              >
                {groupedUpdates[taskName].map((update, index) => (
                  <div key={index} style={{ marginBottom: 12 }}>
                    <Space direction="vertical" size={4}>
                      <Text strong>
                        <UserOutlined /> {update.consultant_name}
                      </Text>
                      <Tag
                        color={getStatusColor(update.status_label)}
                        icon={getStatusIcon(update.status_label)}
                      >
                        {update.status_label} ({update.status_pct}%)
                      </Tag>
                      {update.blockers && (
                        <Tooltip title="Current blockers or issues">
                          <Text type="danger">
                            <WarningOutlined /> {update.blockers}
                          </Text>
                        </Tooltip>
                      )}
                      <Text type="secondary">
                        <CalendarOutlined /> ETA: {update.eta_date || "N/A"}
                      </Text>
                      <Text type="secondary">
                        <ClockCircleOutlined /> Last Updated: {new Date(update.created_at).toLocaleString()}
                      </Text>
                    </Space>
                    {index !== groupedUpdates[taskName].length - 1 && (
                      <Divider style={{ margin: "12px 0" }} />
                    )}
                  </div>
                ))}
              </Card>
            </List.Item>
          )}
        />
      )}
    </div>
  );
}

export default TaskUpdates;
