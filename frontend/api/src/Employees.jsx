
import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = "https://api-s-2y7n.onrender.com";

export default function Employees() {
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        axios.get(`${API_URL}/employees`)
            .then(response => setEmployees(response.data))
            .catch(() => setError("Unable to load employees"))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <p>Loading employees...</p>;
    if (error) return <p>{error}</p>;

    return (
        <main style={{ padding: 24 }}>
            <h1>Employee Management System</h1>

            {employees.map(emp => (
                <section
                    key={emp.id}
                    style={{
                        border: "1px solid #ccc",
                        borderRadius: 8,
                        padding: 16,
                        marginBottom: 12
                    }}
                >
                    <h2>{emp.name}</h2>
                    <p>Employee ID: {emp.id}</p>
                    <p>Department: {emp.department}</p>
                    <p>Designation: {emp.designation}</p>
                    <p>Email: {emp.email}</p>
                    <p>Salary: ₹{emp.salary}</p>

                    <h3>Manager Details</h3>
                    {emp.manager ? (
                        <>
                            <p>{emp.manager.name}</p>
                            <p>{emp.manager.designation}</p>
                        </>
                    ) : (
                        <p>No manager assigned</p>
                    )}
                </section>
            ))}
        </main>
    );
}
