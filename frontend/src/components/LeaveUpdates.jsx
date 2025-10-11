
import React, { useEffect, useState } from "react";
import {
  Card, List, Tag, Typography, Space, Spin, Empty, Button, Tooltip,
} from "antd";
import {
  UserOutlined, CalendarOutlined, WarningOutlined,ClockCircleOutlined, 
} from "@ant-design/icons";
import api from "../api/api";
import { useNavigate } from "react-router-dom";

const { Text, Title } = Typography;

function LeaveUpdates() {
  const [leaveUpdates, setLeaveUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLeaveUpdates = async () => {
      try {
        const res = await api.get("/leave-updates/?state=0");
        const data = res.data;

        const uniqueUpdates = data.reduce((acc, item) => {
          if (!acc[item.consultant_email] || new Date(item.created_at) > new Date(acc[item.consultant_email].created_at)) {
            acc[item.consultant_email] = item;
          }
          return acc;
        }, {});

        setLeaveUpdates(Object.values(uniqueUpdates));
      } catch (err) {
        console.error("Error fetching leave updates:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaveUpdates();
  }, []);

  const handleMailClick = (update) => {
    navigate("/draft-reply", {
      state: {
        task_id: update.task_id,
        consultant_email: update.consultant_email,
        email_subject: `Leave Update for ${update.task_name}`,
        email_body: `${update.summary}`,
      },
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" tip="Loading leave updates..." />
      </div>
    );
  }

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        Leave Updates
      </Title>
      {leaveUpdates.length === 0 ? (
        <Empty description="No leave updates available" />
      ) : (
        <List
          dataSource={leaveUpdates}
          renderItem={(update) => (
            <List.Item>
              <Card
                style={{
                  width: "100%",
                  borderRadius: 12,
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                }}
              >
                <Space direction="vertical" size={8}>
                  <Text strong>
                    <UserOutlined /> {update.consultant_name}
                  </Text>
                  <Text>
                    <b>Task:</b> {update.task_name}
                  </Text>
                  <Tag color="volcano">
                    {update.status_label} ({update.status_pct}%)
                  </Tag>
                  {update.blockers && (
                    <Tooltip title="Blockers">
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
                  <Text>
                    <b>Summary:</b> {update.summary}
                  </Text>
                  <Button
                    type="primary"
                    onClick={() => handleMailClick(update)}
                    style={{ marginTop: 8 }}
                  >
                    Mail
                  </Button>
                </Space>
              </Card>
            </List.Item>
          )}
        />
      )}
    </div>
  );
}

export default LeaveUpdates;
