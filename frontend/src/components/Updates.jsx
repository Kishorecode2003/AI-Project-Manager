import React from "react";
import { Tabs } from "antd";
import TaskUpdates from "./TaskUpdates";
import LeaveUpdates from "./LeaveUpdates";
function Updates() {
  return (
    <div style={{ padding: "24px" }}>
      <Tabs
        defaultActiveKey="task"
        items={[
          {
            key: "task",
            label: "Task Updates",
            children: <TaskUpdates />,
          },
          {
            key: "leave",
            label: "Leave Updates",
            children: <LeaveUpdates />,
          },
        ]}
      />
    </div>
  );
}
export default Updates;
