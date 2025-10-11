import React, { useEffect, useState } from "react";
import { Row, Col, Card, Statistic, List, Modal, Button } from "antd";
import api from "../api/api";

function Dashboard() {
  const [stats, setStats] = useState({
    overdue: [],
    noUpdate: [],
    atRisk: [],
    done: [],
  });
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState("");
  const [modalContent, setModalContent] = useState([]);

  useEffect(() => {
    api.get("/summary/dashboard").then((res) => setStats(res.data));
  }, []);

  const showModal = (title, content) => {
    setModalTitle(title);
    setModalContent(content);
    setModalVisible(true);
  };

  const handleOk = () => {
    setModalVisible(false);
  };

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} md={6}>
        <Card
          hoverable
          style={{ borderLeft: "4px solid #ff4d4f" }}
          actions={[
            <Button type="link" onClick={() => showModal("Overdue Tasks", stats.overdue)}>
              View Tasks
            </Button>,
          ]}
        >
          <Statistic title="Overdue Tasks" value={stats.overdue.length} />
        </Card>
      </Col>
      <Col xs={24} sm={12} md={6}>
        <Card
          hoverable
          style={{ borderLeft: "4px solid #faad14" }}
          actions={[
            <Button type="link" onClick={() => showModal("No Update (48h)", stats.noUpdate)}>
              View Tasks
            </Button>,
          ]}
        >
          <Statistic title="No Update (48h)" value={stats.noUpdate.length} />
        </Card>
      </Col>
      <Col xs={24} sm={12} md={6}>
        <Card
          hoverable
          style={{ borderLeft: "4px solid #1890ff" }}
          actions={[
            <Button type="link" onClick={() => showModal("At Risk", stats.atRisk)}>
              View Tasks
            </Button>,
          ]}
        >
          <Statistic title="At Risk" value={stats.atRisk.length} />
        </Card>
      </Col>
      <Col xs={24} sm={12} md={6}>
        <Card
          hoverable
          style={{ borderLeft: "4px solid #52c41a" }}
          actions={[
            <Button type="link" onClick={() => showModal("Done This Week", stats.done)}>
              View Tasks
            </Button>,
          ]}
        >
          <Statistic title="Done This Week" value={stats.done.length} />
        </Card>
      </Col>

      <Modal
        title={modalTitle}
        visible={modalVisible}
        onOk={handleOk}
        onCancel={handleOk}
        footer={[
          <Button key="back" onClick={handleOk}>
            Close
          </Button>,
        ]}
      >
        <List
          dataSource={modalContent}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                title={item.task_name}
                description={`Assignees: ${item.assignees.join(", ")}`}
              />
            </List.Item>
          )}
        />
      </Modal>
    </Row>
  );
}

export default Dashboard;
