import React, { useEffect, useState } from "react";
import { Table } from "antd";
import api from "../api/api";

function Consultants() {
  const [consultants, setConsultants] = useState([]);

  useEffect(() => {
    api.get("/consultants/")
      .then((res) => {
        console.log("API Response:", res.data); 
        setConsultants(res.data);
      })
      .catch((err) => {
        console.error("API Error:", err);
      });
  }, []);


  return (
    <Table
      rowKey="id"
      dataSource={consultants}
      columns={[
        { title: "Name", dataIndex: "name" },
        { title: "Email", dataIndex: "email" },
      ]}
    />
  );
}

export default Consultants;
