const topics = ["APU", "Hydraulics", "Electrical"];

export function LeftPanel() {
  return (
    <aside className="left-panel" aria-label="Notebook topics">
      <div>
        <p className="eyebrow">Notebook</p>
        <h1>AeroAgent</h1>
      </div>
      <nav className="topic-list" aria-label="Topic list">
        {topics.map((topic) => (
          <button className="topic-button" type="button" key={topic}>
            <span>{topic}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}
