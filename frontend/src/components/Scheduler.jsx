import React, { useState } from "react";
import { Form, Input, TimePicker, Button, Card, message } from "antd";
import api from "../api/api";
import moment from "moment";

function Scheduler() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSave = async (values) => {
    try {
      setLoading(true);
      const payload = {
        task_id: parseInt(values.task_id, 10),
        reminder_time: values.reminder_time.format("HH:mm"),
      };
      await api.post("/scheduler/schedule-reminder", payload);
      message.success(`Reminder scheduled for Task ID ${payload.task_id}`);
      form.resetFields();
    } catch (error) {
      console.error("Error scheduling reminder:", error);
      message.error(
        error.response?.data?.detail || "Failed to schedule reminder"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Task Reminder Scheduler" style={{ maxWidth: 400, margin: "0 auto" }}>
      <Form form={form} onFinish={handleSave} layout="vertical">
        <Form.Item
          name="task_id"
          label="Task ID"
          rules={[{ required: true, message: "Please enter a Task ID" }]}
        >
          <Input placeholder="Enter Task ID" type="number" />
        </Form.Item>

        <Form.Item
          name="reminder_time"
          label="Reminder Time"
          rules={[{ required: true, message: "Please select reminder time" }]}
        >
          <TimePicker format="HH:mm" style={{ width: "100%" }} />
        </Form.Item>

        <Button type="primary" htmlType="submit" loading={loading} block>
          Schedule Reminder
        </Button>
      </Form>
    </Card>
  );
}

export default Scheduler;
