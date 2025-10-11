import React, { useState, useEffect } from "react";
import { Table, Button, Modal, Form, Input, DatePicker, Select, message, Space, Tag } from "antd";
import api from "../api/api";

function Tasks({ refreshKey }) {
  const [tasks, setTasks] = useState([]);
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();

  const fetchTasks = async () => {
    try {
      const res = await api.get("/tasks/");
      setTasks(res.data);
    } catch (err) {
      message.error("Failed to fetch tasks");
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [refreshKey]); 

  const handleCreate = async (values) => {
    try {
      const createResponse = await api.post("/tasks/", values);
      const taskId = createResponse.data.id;

      await api.post("/tasks/send-update", { task_id: taskId });

      message.success("Task created and email sent successfully!");
      fetchTasks();
      setVisible(false);
      form.resetFields();
    } catch (err) {
      message.error("Failed to create task or send email");
      console.error(err);
    }
  };


  return (
    <>
      <Button type="primary" style={{ marginBottom: 16 }} onClick={() => setVisible(true)}>
        + New Task
      </Button>
      <Table
        rowKey="id"
        dataSource={tasks}
        columns={[
          { title: "Task ID", dataIndex: "id", key: "id" },
          { title: "Task Name", dataIndex: "name" },
          { title: "Status", dataIndex: "status" },
          { title: "Start Date", dataIndex: "start_date" },
          { title: "End Date", dataIndex: "end_date" },
          {
            title: "Assignees",
            dataIndex: "assignees",
            render: (assignees) => (
              <>
                {assignees?.map((assignee) => (
                  <Tag key={assignee.email}>{assignee.name}</Tag>
                ))}
              </>
            ),
          },
        ]}
      />
      <Modal
        open={visible}
        title="Create Task"
        onCancel={() => setVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="Task Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="start_date" label="Start Date">
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="end_date" label="End Date">
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.List name="assignees">
              {(fields, { add, remove }) => (
                <>
                  {fields.map(({ key, name, ...restField }) => (
                    <Space key={key} style={{ display: "flex", marginBottom: 8 }} align="baseline">
                      <Form.Item
                        {...restField}
                        name={[name, "name"]}
                        label="Assignee Name"
                        rules={[{ required: true, message: "Missing assignee name" }]}
                      >
                        <Input placeholder="Name" />
                      </Form.Item>
                      <Form.Item
                        {...restField}
                        name={[name, "email"]}
                        label="Email"
                        rules={[
                          { required: true, message: "Missing email" },
                          { type: "email", message: "Invalid email" },
                        ]}
                      >
                        <Input placeholder="Email" />
                      </Form.Item>
                      <Button type="dashed" onClick={() => remove(name)}>
                        Remove
                      </Button>
                    </Space>
                  ))}
                  <Form.Item>
                    <Button type="dashed" onClick={() => add()} block>
                      + Add Assignee
                    </Button>
                  </Form.Item>
                </>
              )}
            </Form.List>
        </Form>
      </Modal>
    </>
  );
}

export default Tasks;
