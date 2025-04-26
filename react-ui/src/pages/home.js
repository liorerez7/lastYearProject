import React from 'react';
import CreateSimpleTestButton from '../components/CreateSimpleTestButton';
import RunMigrationButton from '../components/RunMigrationButton';

export default function Home() {
  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Database Migration & Test UI</h1>
      <CreateSimpleTestButton />
      <RunMigrationButton />
    </div>
  );
}
