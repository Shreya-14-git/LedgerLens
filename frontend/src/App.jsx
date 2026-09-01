import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {  
  
  const [summary, setSummary] = useState(null);
  const [exceptions, setExceptions] = useState([]);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [investigating, setInvestigating] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [transactionResult, setTransactionResult] = useState(null);
  const [auditEvents, setAuditEvents] = useState([]);
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("All");
  const [successMessage, setSuccessMessage] = useState("");
  const [orderIdStatus, setOrderIdStatus] = useState("");
  const [newTransaction, setNewTransaction] = useState({
  order_id: "",
  order_amount: "",
  payment_amount: "",
  payment_status: "Success",
  settlement_amount: "",
  settlement_status: "Settled"
});
  

    useEffect(() => {
    if (selectedTransaction) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [selectedTransaction]);

  async function loadData() {
  try {
    const summaryResponse = await fetch(
      `${API_URL}/summary`
    );

    const exceptionResponse = await fetch(
      `${API_URL}/exceptions`
    );

    const metricsResponse = await fetch(
      `${API_URL}/metrics`
    );

    const auditResponse = await fetch(
      `${API_URL}/audit`
    );

    const summaryData = await summaryResponse.json();
    const exceptionData = await exceptionResponse.json();
    const metricsData = await metricsResponse.json();
    const auditData = await auditResponse.json();

    setSummary(summaryData);
    setExceptions(exceptionData.exceptions);
    setMetrics(metricsData);
    setAuditEvents(auditData.events);

  } catch (error) {
    console.error("Failed to load LedgerLens data:", error);

  } finally {
    setLoading(false);
  }
}

useEffect(() => {
  loadData();
}, []);

  async function investigate(orderId) {
  setInvestigating(true);

  try {
    const response = await fetch(
      `${API_URL}/transaction/${orderId}`
    );

    const data = await response.json();

    if (!response.ok || data.error) {
      console.error("Investigation failed:", data);
      alert(data.error || "Failed to investigate transaction");
      return;
    }

    setSelectedTransaction(data);

  } catch (error) {
    console.error(
      "Failed to investigate transaction:",
      error
    );
  } finally {
    setInvestigating(false);
  }
}

async function checkOrderId(orderId) {
  if (!orderId.trim()) {
    setOrderIdStatus("");
    return;
  }

  try {
    const response = await fetch(
      `${API_URL}/check-order/${orderId}`
    );

    const data = await response.json();

    if (data.exists) {
      setOrderIdStatus("exists");
    } else {
      setOrderIdStatus("available");
    }
  } catch (error) {
    console.error("Failed to check Order ID:", error);
    setOrderIdStatus("");
  }
}
async function addTransaction(e) {
  e.preventDefault();

  try {
    const response = await fetch(`${API_URL}/transaction`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        order_id: newTransaction.order_id,
        order_amount: Number(newTransaction.order_amount),
        payment_amount:
          newTransaction.payment_amount === ""
            ? null
            : Number(newTransaction.payment_amount),
        payment_status: newTransaction.payment_status,
        settlement_amount:
          newTransaction.settlement_amount === ""
            ? null
            : Number(newTransaction.settlement_amount),
        settlement_status: newTransaction.settlement_status
      })
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(
        data.detail ||
        data.error ||
        "Failed to add transaction"
      );
    }

    console.log("New transaction:", data);

    setTransactionResult(data);
    setSelectedTransaction(data);

    setSuccessMessage(
      "Transaction added successfully and analyzed by AI"
    );

    setShowAddTransaction(false);

    await loadData();

    setNewTransaction({
      order_id: "",
      order_amount: "",
      payment_amount: "",
      payment_status: "Success",
      settlement_amount: "",
      settlement_status: "Settled"
    });

  } catch (error) {
    console.error("Failed to add transaction:", error);

    alert(error.message || "Failed to add transaction");
  }
}

  function closeInvestigation() {
    setSelectedTransaction(null);
  }
  const filteredExceptions = exceptions.filter((item) => {

  // Risk card filter
  if (riskFilter === "HIGH" &&
      item.status !== "Settlement Mismatch") {
    return false;
  }

  if (riskFilter === "MEDIUM" &&
      item.status !== "Missing Settlement") {
    return false;
  }

  if (
    riskFilter === "LOW" &&
    item.status !== "Missing Payment" &&
    item.status !== "Duplicate Payment"
  ) {
    return false;
  }

  // Search filter
  const matchesSearch =
    item.order_id
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

  // Status dropdown filter
  const matchesStatus =
    filterStatus === "All" ||
    item.status === filterStatus;

  return matchesSearch && matchesStatus;
});

  if (loading) {
    return (
      <div className="loading">
        Loading LedgerLens...
      </div>
    );
  }

  return (
    <div className="app">
      {successMessage && (
  <div className="success-message">
    <span>✓</span>
    {successMessage}
  </div>
)}

      {/* HEADER */}
      <header className="header">
        <div>
          <h1>LedgerLens</h1>
          <p>AI Finance Controller</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Active
        </div>
      </header>


      {/* KPI CARDS */}
      <section className="stats">

        <div className="card">
          <p>Transactions</p>
          <h2>{summary.total_transactions}</h2>
          <span>Total records processed</span>
        </div>

        <div className="card success">
          <p>Matched</p>
          <h2>{summary.matched}</h2>
          <span>Successfully reconciled</span>
        </div>

        <div className="card warning">
          <p>Exceptions</p>
          <h2>{summary.exceptions}</h2>
          <span>Require attention</span>
        </div>
        <div className="card risk">
  <p>Exception Value</p>

  <h2>
    ₹{metrics
      ? metrics.exception_value.toLocaleString("en-IN")
      : "0"}
  </h2>

  <span>Value requiring investigation</span>
</div>

        <div className="card">
          <p>Match Rate</p>
          <h2>{summary.match_rate}%</h2>
          <span>Reconciliation accuracy</span>
        </div>

      </section>
            
      {/* EXCEPTION BREAKDOWN */}

      <section className="panel breakdown-panel">

        <div className="panel-header">

          <div>
            <h2>Exception Breakdown</h2>
            <p>Why transactions require attention</p>
          </div>

          <span className="exception-count">
            {metrics?.exceptions || 0} total
            
          </span>

        </div>


        <div className="breakdown-list">

          {metrics &&
            Object.entries(metrics.exception_breakdown).map(
              ([type, count]) => {

                const percentage =
                  (count / metrics.exceptions) * 100;

                return (
                  <div
                    className="breakdown-item"
                    key={type}
                  >

                    <div className="breakdown-info">

                      <span>{type}</span>

                      <strong>{count}</strong>

                    </div>

                    <div className="progress-bar">

                      <div
                        className="progress-fill"
                        style={{
                          width: `${percentage}%`
                        }}
                      ></div>

                    </div>

                    <small>
                      {percentage.toFixed(1)}% of exceptions
                    </small>

                  </div>
                );
              }
            )}

        </div>

      </section>
            


      {/* RISK OVERVIEW */}

      <section className="panel risk-panel">

        <div className="panel-header">

          <div>
            <h2>Risk Overview</h2>
            <p>Prioritization of financial exceptions</p>
          </div>

        </div>
<div className="risk-grid">
        {/* HIGH RISK */}
<div
  className={`risk-card high-risk ${
    riskFilter === "HIGH" ? "active-risk" : ""
  }`}
  onClick={() => setRiskFilter("HIGH")}
>
  <span>HIGH RISK</span>

  <strong>
    {metrics?.exception_breakdown?.["Settlement Mismatch"] || 0}
  </strong>

  <small>Settlement mismatches</small>
</div>


{/* MEDIUM RISK */}
<div
  className={`risk-card medium-risk ${
    riskFilter === "MEDIUM" ? "active-risk" : ""
  }`}
  onClick={() => setRiskFilter("MEDIUM")}
>
  <span>MEDIUM RISK</span>

  <strong>
    {metrics?.exception_breakdown?.["Missing Settlement"] || 0}
  </strong>

  <small>Missing settlements</small>
</div>


{/* LOW RISK */}
<div
  className={`risk-card low-risk ${
    riskFilter === "LOW" ? "active-risk" : ""
  }`}
  onClick={() => setRiskFilter("LOW")}
>
  <span>LOW RISK</span>

  <strong>
    {(metrics?.exception_breakdown?.["Missing Payment"] || 0) +
      (metrics?.exception_breakdown?.["Duplicate Payment"] || 0)}
  </strong>

  <small>Payment-related exceptions</small>
</div>
</div>
<button
  className="risk-reset"
  onClick={() => setRiskFilter("ALL")}
>
  Show All Exceptions
</button>
        

      </section>
      {/* AUDIT TRAIL */}

<section className="panel audit-panel">

  <div className="panel-header">

    <div>
      <h2>Audit Trail</h2>
      <p>Recent reconciliation activity</p>
    </div>

    <span className="exception-count">
      {auditEvents.length} events
    </span>

  </div>

  <div className="audit-list">

    {auditEvents.map((item, index) => (

      <div className="audit-item" key={index}>

        <div className="audit-time">
          {item.time}
        </div>

        <div className="audit-dot"></div>

        <div className="audit-content">

          <strong>
            {item.event}
          </strong>

          <span>
            {item.details}
          </span>

        </div>

      </div>

    ))}

  </div>

</section>

      {/* EXCEPTIONS */}
      <section className="panel">

        <div className="panel-header">

  <div>
    <h2>Financial Exceptions</h2>
    <p>
      Transactions requiring investigation
    </p>
  </div>

  <span className="exception-count">
    {filteredExceptions.length} shown / {exceptions.length} exceptions
  </span>
  <button
  className="add-transaction-button"
  onClick={() => setShowAddTransaction(true)}
>
  + Add Transaction
</button>

</div>

<div className="exception-controls">

  <div className="search-box">
  <span>⌕</span>

  <input
    type="text"
    placeholder="Search Order ID..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
  />
</div>

  <select
    value={filterStatus}
    onChange={(e) => setFilterStatus(e.target.value)}
  >
    <option value="All">All Issues</option>
    <option value="Missing Payment">
      Missing Payment
    </option>
    <option value="Missing Settlement">
      Missing Settlement
    </option>
    <option value="Settlement Mismatch">
      Settlement Mismatch
    </option>
    <option value="Duplicate Payment">
      Duplicate Payment
    </option>
  </select>
  {(searchTerm || filterStatus !== "All" || riskFilter !== "ALL") && (
  <button
    className="clear-filters"
    onClick={() => {
      setSearchTerm("");
      setFilterStatus("All");
      setRiskFilter("ALL");
    }}
  >
    Clear Filters
  </button>
)}

</div>



        <div className="table-container">

          <table>

            <thead>
              <tr>
                <th>Order ID</th>
                <th>Amount</th>
                <th>Issue</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
  {filteredExceptions.length === 0 ? (
    <tr>
      <td colSpan="4" className="empty-state">
  <strong>No exceptions found</strong>
  <span>
    Try changing your search or filter criteria.
  </span>
</td>
    </tr>
  ) : (
    filteredExceptions.map((item) => (
      <tr key={item.order_id}>

        <td className="order-id">
          {item.order_id}
        </td>

       <td>
  ₹{(item.amount ?? item.order_amount ?? 0).toLocaleString("en-IN")}
</td>
        <td>
          <span
            className={`badge ${getStatusClass(item.status)}`}
          >
            {item.status}
          </span>
        </td>

        <td>
          <button
            className="view-button"
            onClick={() => investigate(item.order_id)}
          >
            Investigate
          </button>
        </td>

      </tr>
    ))
  )}
</tbody>

          </table>

        </div>

      </section>
      {showAddTransaction && (
  <div className="add-transaction-overlay">

    <div className="add-transaction-panel">

      <div className="add-transaction-header">
        <div>
          <p className="small-label">
            NEW TRANSACTION
          </p>

          <h2>Add Transaction</h2>
        </div>

        <button
          className="close-button"
          onClick={() => setShowAddTransaction(false)}
        >
          ×
        </button>
      </div>

      <form onSubmit={addTransaction}>

        <div className="form-grid">

<div className="form-group">
  <label htmlFor="order_id">Order ID</label>

  <input
    id="order_id"
    type="text"
    placeholder="Enter Order ID (e.g. ORD0010)"
    value={newTransaction.order_id}
    onChange={(e) => {
      const value = e.target.value.toUpperCase();

      setNewTransaction({
        ...newTransaction,
        order_id: value
      });

      checkOrderId(value);
    }}
  />

  {orderIdStatus === "exists" && (
    <div className="order-status error">
      ⚠ Order ID already exists
    </div>
  )}

  {orderIdStatus === "available" && (
    <div className="order-status success">
      ✓ Order ID is available
    </div>
  )}

  {!newTransaction.order_id && (
    <small className="input-hint">
      Enter a unique Order ID to continue
    </small>
  )}
</div>

          <div className="form-group">
            <label>Order Amount</label>
            <input
              type="number"
              placeholder="5000"
              value={newTransaction.order_amount}
              onChange={(e) =>
                setNewTransaction({
                  ...newTransaction,
                  order_amount: e.target.value
                })
              }
              required
            />
          </div>

          <div className="form-group">
            <label>Payment Amount</label>
            <input
              type="number"
              placeholder="5000"
              value={newTransaction.payment_amount}
              onChange={(e) =>
                setNewTransaction({
                  ...newTransaction,
                  payment_amount: e.target.value
                })
              }
            />
          </div>

          <div className="form-group">
            <label>Payment Status</label>
            <select
              value={newTransaction.payment_status}
              onChange={(e) =>
                setNewTransaction({
                  ...newTransaction,
                  payment_status: e.target.value
                })
              }
            >
              <option value="Success">Success</option>
              <option value="Failed">Failed</option>
              <option value="Pending">Pending</option>
            </select>
          </div>

          <div className="form-group">
            <label>Settlement Amount</label>
            <input
              type="number"
              placeholder="4700"
              value={newTransaction.settlement_amount}
              onChange={(e) =>
                setNewTransaction({
                  ...newTransaction,
                  settlement_amount: e.target.value
                })
              }
            />
          </div>

          <div className="form-group">
            <label>Settlement Status</label>
            <select
              value={newTransaction.settlement_status}
              onChange={(e) =>
                setNewTransaction({
                  ...newTransaction,
                  settlement_status: e.target.value
                })
              }
            >
              <option value="Settled">Settled</option>
              <option value="Pending">Pending</option>
              <option value="Failed">Failed</option>
            </select>
          </div>

        </div>

        <div className="form-actions">

          <button
            type="button"
            className="cancel-button"
            onClick={() => setShowAddTransaction(false)}
          >
            Cancel
          </button>

          <button
  type="submit"
  disabled={orderIdStatus === "exists"}
>
  Add Transaction
</button>

        </div>

      </form>

    </div>

  </div>
)}


      {/* INVESTIGATION PANEL */}

      {selectedTransaction && (

        <div className="overlay">

          <div className="investigation-panel">

            <div className="investigation-header">

              <div>
                <p className="small-label">
                  TRANSACTION INVESTIGATION
                </p>

                <h2>
                  {selectedTransaction.order_id}
                </h2>
              </div>

              <button
                className="close-button"
                onClick={closeInvestigation}
              >
                ×
              </button>

            </div>


            {/* AMOUNTS */}

            <div className="transaction-grid">

              <div className="transaction-card">
                <span>Order Amount</span>
                <strong>
  ₹{(
    selectedTransaction.order_amount ??
    selectedTransaction.amount ??
    0
  ).toLocaleString("en-IN")}
</strong>
              </div>


              <div className="transaction-card">
                <span>Payment Amount</span>

                <strong>
  {selectedTransaction.payment_amount != null
    ? `₹${selectedTransaction.payment_amount.toLocaleString("en-IN")}`
    : "Missing"}
</strong>
              </div>


              <div className="transaction-card">
                <span>Settlement Amount</span>

               <strong>
  {selectedTransaction.settlement_amount != null
    ? `₹${selectedTransaction.settlement_amount.toLocaleString("en-IN")}`
    : "Missing"}
</strong>
              </div>

            </div>


            {/* STATUS */}

            <div className="investigation-section">

              <p className="small-label">
                RECONCILIATION STATUS
              </p>

              <span
                className={`badge large ${getStatusClass(
                  selectedTransaction.status
                )}`}
              >
                {selectedTransaction.status}
              </span>

            </div>


            {/* DIFFERENCE */}

            {selectedTransaction.difference !== null && (

              <div className="difference-box">

                <span>Amount Difference</span>

                <strong>
                  ₹
                  {Math.abs(
                    selectedTransaction.difference
                  ).toLocaleString("en-IN")}
                </strong>

              </div>

            )}


            {/* AI ANALYSIS */}

<div className="ai-analysis">

  <div className="ai-header">
    <div>
      <p className="small-label">
        AI FINANCE ANALYSIS
      </p>

      <h3>AI Investigation</h3>
    </div>

    <span className="ai-badge">
      AI
    </span>
  </div>


  {/* SUMMARY */}

  <div className="ai-summary">
    <p>
      {selectedTransaction.ai_analysis?.summary || "No AI analysis available"}
    </p>
  </div>


  {/* LIKELY CAUSES */}

  <div className="ai-causes">

    <p className="small-label">
      LIKELY CAUSES
    </p>

    <ul>
      {selectedTransaction.ai_analysis?.likely_causes?.map((cause, index) => (
          <li key={index}>
            {cause}
          </li>
        )
      )}
    </ul>

  </div>


  {/* CONFIDENCE */}

  <div className="ai-confidence">

    <span>Confidence</span>

    <strong>
      {selectedTransaction.ai_analysis?.confidence ?? "N/A"}
    </strong>

  </div>


  {/* RECOMMENDATION */}

  <div className="recommendation">

    <p className="small-label">
      RECOMMENDED ACTION
    </p>

    <p>
      {selectedTransaction.ai_analysis?.recommended_action || "No recommendation available"}
    </p>

  </div>

</div>
      </div>
    </div>
  )}

  <footer>
    LedgerLens • Finance operations intelligence
  </footer>

</div>
  );


function getStatusClass(status) {

  if (status === "Missing Payment") {
    return "danger";
  }

  if (status === "Missing Settlement") {
    return "warning";
  }

  if (status === "Settlement Mismatch") {
    return "mismatch";
  }

  if (status === "Duplicate Payment") {
    return "duplicate";
  }

  return "";
}
}
export default App;