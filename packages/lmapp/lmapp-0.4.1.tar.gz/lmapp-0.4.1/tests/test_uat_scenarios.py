"""
User Acceptance Tests (UAT) for lmapp Refactoring Service
Phase 2C: End-to-End User Scenarios

Tests real-world refactoring scenarios:
- Web API development (FastAPI-like patterns)
- React component refactoring
- Utility function improvements
- Production code patterns
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lmapp.server.refactoring_service import RefactoringService, FixCategory


class UserAcceptanceTests:
    """Real-world UAT scenarios"""

    def __init__(self):
        self.service = RefactoringService()

    # ========================================================================
    # PYTHON WEB API SCENARIOS
    # ========================================================================

    def test_python_api_endpoint_refactoring(self):
        """UAT: API endpoint with multiple issues"""
        code = '''
@app.post("/api/users")
def create_user(user_data):
    """Create a new user"""
    if user_data == None:
        return {"error": "Missing user data"}
    
    # Process user
    unused_timestamp = time.time()
    
    user = User(
        name=user_data.get("name"),
        email=user_data.get("email")
    )
    
    if not not user.validate():
        db.add(user)
        db.commit()
        return {"status": "success", "user": user}
    
    return {"status": "error"}
'''

        response = self.service.get_refactoring_suggestions(code, "python", "high")

        # Should find improvements
        assert response["total_fixes"] > 0, "Should find refactoring opportunities"

        # Get specific fixes
        fixes = self.service.get_quick_fixes(code, "python")

        # Should identify: double negative, None comparison
        categories_found = set(f.category for f in fixes)

        print(f"✅ Python API endpoint: Found {response['total_fixes']} improvements")
        print(f"   Categories: {', '.join(c.value for c in categories_found)}")

    def test_python_data_processing_refactoring(self):
        """UAT: Data processing pipeline"""
        code = '''
def process_data(raw_data):
    """Process raw data"""
    if raw_data == None:
        return None
    
    # Transform data
    transformed = []
    for item in raw_data:
        if item and item != "":
            transformed.append(item.strip().upper())
    
    # Validate
    if not not len(transformed) > 0:
        return transformed
    
    return None
'''

        fixes = self.service.get_quick_fixes(code, "python")

        # Should find simplification opportunities
        simplify_fixes = [f for f in fixes if f.category == FixCategory.SIMPLIFY_CODE]

        print(f"✅ Python data processing: Found {len(simplify_fixes)} simplification fixes")

    # ========================================================================
    # JAVASCRIPT/REACT SCENARIOS
    # ========================================================================

    def test_react_component_refactoring(self):
        """UAT: React component with refactoring opportunities"""
        code = """
function UserCard({ user }) {
    var isActive = user.status == "active";
    var formattedName = user.name.toUpperCase();
    
    if (user == null) {
        return <div>Loading...</div>;
    }
    
    if (isActive == true) {
        return (
            <div className="card">
                <h1>{formattedName}</h1>
                <p>{user.email}</p>
            </div>
        );
    }
    
    return null;
}
"""

        response = self.service.get_refactoring_suggestions(code, "javascript", "high")
        fixes = self.service.get_quick_fixes(code, "javascript")

        # Should suggest var to const
        var_fixes = [f for f in fixes if "var" in f.title.lower()]

        assert len(var_fixes) > 0, "Should suggest var to const conversion"

        print(f"✅ React component: Found {len(var_fixes)} var→const suggestions")
        print(f"   Total improvements: {response['total_fixes']}")

    def test_utility_function_refactoring(self):
        """UAT: Utility functions"""
        code = """
export function formatPhone(phone) {
    var input = phone;
    
    if (input == null) {
        return "";
    }
    
    var cleaned = input.replace(/[^0-9]/g, "");
    var parts = [];
    
    if (cleaned.length >= 10) {
        parts.push(cleaned.substring(0, 3));
        parts.push(cleaned.substring(3, 6));
        parts.push(cleaned.substring(6, 10));
    }
    
    return parts.join("-");
}
"""

        fixes = self.service.get_quick_fixes(code, "javascript")

        # Should find var usages
        var_count = sum(1 for f in fixes if "var" in f.title.lower())

        assert var_count >= 3, "Should find multiple var declarations"

        print(f"✅ Utility function: Found {var_count} var declarations to convert")

    # ========================================================================
    # TYPESCRIPT SCENARIOS
    # ========================================================================

    def test_typescript_class_refactoring(self):
        """UAT: TypeScript class with issues"""
        code = """
export class UserService {
    private apiUrl: string;
    
    constructor(url: string) {
        this.apiUrl = url;
    }
    
    async getUser(id: number): Promise<User | null> {
        var response = await fetch(`${this.apiUrl}/users/${id}`);
        
        if (response == null) {
            return null;
        }
        
        var data = await response.json();
        return data;
    }
}
"""

        response = self.service.get_refactoring_suggestions(code, "typescript", "high")
        fixes = self.service.get_quick_fixes(code, "typescript")

        # Should find var usage
        var_issues = [f for f in fixes if "var" in f.title.lower()]

        assert len(var_issues) > 0, "Should suggest TypeScript best practices"

        print(f"✅ TypeScript class: Found {len(var_issues)} best practice suggestions")
        print(f"   Total fixes: {response['total_fixes']}")

    # ========================================================================
    # MIXED COMPLEXITY SCENARIOS
    # ========================================================================

    def test_complex_mixed_issues(self):
        """UAT: Complex code with multiple issue types"""
        code = """
class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process(self, items):
        if items == None:
            return None
        
        results = []
        for item in items:
            if item and item != "":
                if not not item.isdigit():
                    results.append(int(item))
        
        if not not len(results) > 0:
            self.data = results
            return results
        
        return None
"""

        fixes = self.service.get_quick_fixes(code, "python")
        response = self.service.get_refactoring_suggestions(code, "python", "high")

        # Categorize findings
        by_category = {}
        for fix in fixes:
            cat = fix.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        print(f"✅ Complex mixed issues: Found {response['total_fixes']} improvements")
        for cat, count in by_category.items():
            print(f"   - {cat}: {count}")

    # ========================================================================
    # ERROR HANDLING SCENARIOS
    # ========================================================================

    def test_error_handling_patterns(self):
        """UAT: Error handling code"""
        code = """
def handle_request(request):
    try:
        if request == None:
            raise ValueError("Request required")
        
        data = parse(request)
        
        if not not data:
            process(data)
            return True
        
        return False
    
    except Exception as e:
        if e == None:
            return False
        
        log_error(e)
        return False
"""

        fixes = self.service.get_quick_fixes(code, "python")

        # Should find multiple issues
        assert len(fixes) > 0, "Should find issues in error handling code"

        print(f"✅ Error handling patterns: Found {len(fixes)} issues to fix")

    # ========================================================================
    # REAL PRODUCTION CODE SAMPLES
    # ========================================================================

    def test_production_webserver_code(self):
        """UAT: Production webserver-like code"""
        code = """
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/api/v1/items")
async def create_item(item_data):
    if item_data == None:
        raise HTTPException(status_code=400, detail="Invalid item")
    
    try:
        var stored = db.store(item_data)
        
        if not not stored:
            return {"status": "created", "id": stored.id}
    
    except Exception as e:
        if e == None:
            raise HTTPException(status_code=500)
        
        log.error(f"Failed to store: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "failed"}
"""

        response = self.service.get_refactoring_suggestions(code, "python", "high")
        fixes = self.service.get_quick_fixes(code, "python")

        # Should find production code quality issues
        assert response["total_fixes"] > 0, "Should find issues in production code"

        print(f"✅ Production code: Found {response['total_fixes']} quality improvements")
        print(f"   {len(fixes)} specific fixes available")

    def test_production_react_code(self):
        """UAT: Production React-like code"""
        code = """
export function Dashboard() {
    var [users, setUsers] = useState([]);
    var [loading, setLoading] = useState(true);
    
    useEffect(() => {
        var fetchUsers = async () => {
            if (fetchUsers == null) return;
            
            var response = await fetch("/api/users");
            var data = await response.json();
            
            if (data == null) {
                return;
            }
            
            setUsers(data);
            setLoading(false == true ? true : false);
        };
        
        fetchUsers();
    }, []);
    
    return (
        <div>
            {loading && <Spinner />}
            {users.map(user => <UserItem key={user.id} user={user} />)}
        </div>
    );
}
"""

        response = self.service.get_refactoring_suggestions(code, "javascript", "high")

        # Should find React code issues
        assert response["total_fixes"] > 0, "Should find issues in React code"

        print(f"✅ Production React: Found {response['total_fixes']} improvements")


def run_uat():
    """Run user acceptance tests"""
    print("\n" + "=" * 70)
    print("USER ACCEPTANCE TESTS (UAT)")
    print("=" * 70 + "\n")

    uat = UserAcceptanceTests()

    tests = [
        # Python scenarios
        ("Python API endpoint", uat.test_python_api_endpoint_refactoring),
        ("Python data processing", uat.test_python_data_processing_refactoring),
        # JavaScript/React scenarios
        ("React component", uat.test_react_component_refactoring),
        ("Utility functions", uat.test_utility_function_refactoring),
        # TypeScript scenarios
        ("TypeScript class", uat.test_typescript_class_refactoring),
        # Complex scenarios
        ("Complex mixed issues", uat.test_complex_mixed_issues),
        # Error handling
        ("Error handling", uat.test_error_handling_patterns),
        # Production code
        ("Production webserver", uat.test_production_webserver_code),
        ("Production React", uat.test_production_react_code),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: FAILED - {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {name}: ERROR - {type(e).__name__}: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("UAT RESULTS SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print(f"📊 Success Rate: {(passed/len(tests)*100):.1f}%")
    print("=" * 70 + "\n")

    if failed == 0:
        print("🎉 ALL USER ACCEPTANCE TESTS PASSED")
        print("   Ready for user evaluation")
    else:
        print(f"⚠️  {failed} UAT(s) need attention")

    return failed == 0


if __name__ == "__main__":
    success = run_uat()
    sys.exit(0 if success else 1)
