
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Typography, Form, Input, Button, Card, message, Space,
} from "antd";
import api from "../api/api";

const { Title, Text } = Typography;
const { TextArea } = Input;

function DraftReplyTab() {
  const location = useLocation();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [reply, setReply] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedReply, setEditedReply] = useState({
    subject: "",
    body: "",
    consultant_email: "",
  });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (location.state) {
      console.log("Received state:", location.state); 
      form.setFieldsValue({
        task_id: location.state.task_id,
        consultant_email: location.state.consultant_email,
        email_subject: location.state.email_subject,
        email_body: location.state.email_body,
      });
      setEditedReply({
        subject: location.state.email_subject,
        body: location.state.email_body,
        consultant_email: location.state.consultant_email,
      });
    }
  }, [location.state, form]);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const res = await api.post("/tasks/draft-reply", values);
      setReply(res.data);
      setEditedReply({
        subject: res.data.reply_subject,
        body: res.data.reply_body,
        consultant_email: res.data.consultant_email || values.consultant_email,
      });
      setIsEditing(false);
      message.success("Draft reply generated successfully!");
    } catch (err) {
      message.error("Failed to generate draft reply.");
      console.error("Error generating draft reply:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditToggle = () => {
    setIsEditing(!isEditing);
  };

  const handleSendMail = async () => {
    setSending(true);
    try {
      const payload = {
        task_id: form.getFieldValue("task_id"),
        consultant_email: editedReply.consultant_email,
        reply_subject: editedReply.subject,
        reply_body: editedReply.body,
      };
      await api.post("/tasks/send-mail", payload);
      message.success("Mail sent successfully!");
      navigate("/updates");
    } catch (err) {
      message.error("Failed to send mail.");
      console.error("Error sending mail:", err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ padding: "24px" }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        Draft Reply
      </Title>
      <Card bordered={false} style={{ borderRadius: 12 }}>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item
            name="task_id"
            label="Task ID"
            rules={[{ required: true, message: "Please input the Task ID!" }]}
          >
            <Input type="number" placeholder="Enter Task ID" disabled />
          </Form.Item>
          <Form.Item
            name="consultant_email"
            label="Consultant Email"
            rules={[{ required: true, message: "Please input the Consultant Email!" }]}
          >
            <Input type="email" placeholder="Enter Consultant Email" disabled />
          </Form.Item>
          <Form.Item
            name="email_subject"
            label="Email Subject"
            rules={[{ required: true, message: "Please input the Email Subject!" }]}
          >
            <Input placeholder="Enter Email Subject" disabled />
          </Form.Item>
          <Form.Item
            name="email_body"
            label="Email Body"
            rules={[{ required: true, message: "Please input the Email Body!" }]}
          >
            <TextArea rows={6} placeholder="Enter Email Body" disabled />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              Draft
            </Button>
          </Form.Item>
        </Form>
      </Card>
      {reply && (
        <Card
          title="Generated Reply"
          bordered={false}
          style={{ marginTop: 24, borderRadius: 12 }}
          extra={
            <Space>
              <Button onClick={handleEditToggle}>
                {isEditing ? "Cancel" : "Edit"}
              </Button>
              <Button
                type="primary"
                onClick={handleSendMail}
                loading={sending}
                disabled={!editedReply.body || !editedReply.subject}
              >
                Send Mail
              </Button>
            </Space>
          }
        >
          <Text strong>Consultant Email:</Text>
          <div
            style={{
              marginTop: 6,
              marginBottom: 12,
              background: "#f9f9f9",
              padding: "8px 12px",
              borderRadius: 6,
              border: "1px solid #e8e8e8",
            }}
          >
            {editedReply.consultant_email}
          </div>
          <Text strong>Subject:</Text>
          {isEditing ? (
            <Input
              value={editedReply.subject}
              onChange={(e) =>
                setEditedReply({ ...editedReply, subject: e.target.value })
              }
              style={{ marginTop: 6, marginBottom: 12 }}
            />
          ) : (
            <div style={{ marginTop: 6, marginBottom: 12 }}>
              {editedReply.subject}
            </div>
          )}
          <Text strong>Body:</Text>
          {isEditing ? (
            <TextArea
              rows={8}
              value={editedReply.body}
              onChange={(e) =>
                setEditedReply({ ...editedReply, body: e.target.value })
              }
              style={{ marginTop: 6 }}
            />
          ) : (
            <div
              style={{
                whiteSpace: "pre-wrap",
                marginTop: 8,
                fontFamily: "inherit",
                lineHeight: 1.6,
              }}
            >
              {editedReply.body}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

export default DraftReplyTab;
