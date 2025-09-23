# Claude Development Memory & Lessons Learned

## Repository Context
**Project**: Workflow Builder Application  
**Stack**: React Flow + FastAPI + PostgreSQL + Docker  
**Last Updated**: 2025-09-09  
**Claude Model**: Sonnet 4 (claude-sonnet-4-20250514)

## 🧠 AI Development Memory

### Critical Issues Discovered & Resolved

#### 1. React Flow Parameter Synchronization Bug (CRITICAL)
**Issue**: Node parameter changes in UI don't sync to workflow state, causing stale data to be saved and executed.

**Root Cause**: React components used isolated `useState` without updating ReactFlow's global node data structure.

**Solution Pattern**:
```typescript
// ✅ CORRECT: Bidirectional state synchronization
const [localState, setLocalState] = useState(data.parameter || defaultValue)

// Update both local and global state
const handleParameterChange = useCallback((newValue: any) => {
  setLocalState(newValue)
  setNodes((nodes) =>
    nodes.map((node) =>
      node.id === id
        ? { ...node, data: { ...node.data, parameter: newValue } }
        : node
    )
  )
}, [id, setNodes])

// Sync external changes to local state
useEffect(() => {
  setLocalState(data.parameter || defaultValue)
}, [data.parameter])
```

**Files Affected**:
- `frontend/src/components/workflow/nodes/GetBestSellingAsinsNode.tsx`
- `frontend/src/components/workflow/nodes/GetAsinByIndexNode.tsx`

**User Feedback**: "when i change the parameters in the nodes and press save then run the parameters don't update this is a frontend issue as i can see the data being passed through to save is the stale data"

---

#### 2. Database Seeding Reliability Issues
**Issue**: Seed data not appearing after `./setup.sh` runs.

**Root Cause**: Backend service not fully ready when seeding script executes.

**Solution**: Enhanced setup.sh with proper service orchestration:
```bash
# Start backend and wait
docker-compose up -d backend
sleep 15  # Allow backend to fully initialize
docker-compose exec -T backend python seed_data.py
```

**Lesson**: Database operations require service readiness checks, not just container startup.

---

#### 3. Node ID Consistency Requirements
**Issue**: Workflow node IDs must be consistent between frontend components and backend seed data.

**Solution**: Used nuclear reset approach when changing node IDs:
```bash
docker-compose down -v  # Destroy all data
./setup.sh              # Fresh setup with new IDs
```

**Pattern**: When making structural changes to workflows, always use nuclear reset approach.

---

### Development Workflow Patterns

#### Nuclear Reset Strategy
**When to Use**: Database schema changes, major workflow structure changes, or persistent data inconsistencies.

**Process**:
1. `docker-compose down -v` (destroys all volumes and data)
2. `./setup.sh` (fresh setup with migrations and seeding)
3. `./run.sh` (start clean application)

**Why**: More reliable than incremental migrations during development.

#### Parameter Change Testing
**Pattern**: After implementing node parameter synchronization, verify:
1. Change parameter in UI
2. Save workflow
3. Run workflow
4. Verify execution uses new parameter values (not stale ones)

## 🔧 Technical Implementation Notes

### React Flow State Architecture
**Key Insight**: React Flow maintains global state separate from individual component state. Components must actively sync changes bidirectionally.

**Common Mistake**: Only updating component state without syncing to ReactFlow's nodes array.

**Correct Pattern**: Always use `setNodes` callback to update global state when local parameters change.

### Workflow Execution Flow
1. **Get Best Selling ASINs**: Returns array of ASINs sorted by sales_amount DESC
2. **Get ASIN by Index**: Selects single ASIN from input array by index
3. **Get ASIN Details**: Returns full product details for single ASIN

**Data Types**:
- ASINs: Array of strings `["B08N5WRWNW", "B085HV4BZ6"]`
- Single ASIN: String `"B08N5WRWNW"`
- Product Details: Object with title, description, bullet_points

### Authentication & Authorization
- **Demo Credentials**: `demo@example.com` / `demo123`
- **JWT Storage**: localStorage with 'auth-token' key
- **Route Protection**: All workflow and product routes require authentication
- **API Integration**: Axios interceptors handle token attachment and 401 redirects

## 📚 Lessons Learned

### 1. State Management in React Flow Applications
**Lesson**: React Flow components need special attention to state synchronization.
**Implication**: Always implement bidirectional state sync patterns for any editable parameters.

### 2. Docker Service Dependencies
**Lesson**: Container startup ≠ service readiness
**Implication**: Always implement proper service health checks and delays in setup scripts.

### 3. Development vs Production Data Management
**Lesson**: Nuclear reset is acceptable (and often preferred) for development environments.
**Implication**: Prioritize development velocity over data preservation in local environments.

### 4. User Feedback Integration
**Lesson**: Users can identify subtle state synchronization issues that automated tests might miss.
**Implication**: User-reported "stale data" issues often indicate state synchronization problems.

## 🧪 Testing Strategies

### Integration Test Pattern
**Workflow Execution Testing**:
1. Create workflow with specific parameters
2. Execute workflow via API
3. Verify results match expected parameter values
4. Confirm no stale data in execution

**Example Test Cases**:
- Modify topCount from 10 to 3, verify only 3 ASINs returned
- Change index from 0 to 1, verify second ASIN selected
- Update parameters multiple times, verify latest values used

### Frontend Build Verification
**Pattern**: Always run `npm run build` after React Flow component changes to catch TypeScript errors early.

## 🔄 Common Development Patterns

### API Hook Pattern
```typescript
export const useDataHook = () => {
  return useQuery({
    queryKey: ['data-key'],
    queryFn: async () => {
      const response = await api.get('/endpoint/')
      return response.data as DataType[]
    },
  })
}
```

### Page Component Pattern
```typescript
export const MyPage: React.FC = () => {
  const { data, isLoading, error } = useDataHook()
  
  if (isLoading) return <LoadingState />
  if (error) return <ErrorState error={error} />
  return <SuccessState data={data} />
}
```

### FastAPI Route Pattern
```python
@router.get("/", response_model=List[schemas.Model])
def get_items(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Model).all()
```

## 🐛 Debugging Strategies

### React Flow Issues
1. **Check React Developer Tools**: Verify node data in ReactFlow state
2. **Console Log State Changes**: Monitor both local and global state updates
3. **Network Tab**: Verify API calls contain expected parameter values
4. **Component Re-renders**: Ensure useEffect dependencies are correct

### Backend Issues
1. **FastAPI Docs**: Use `/docs` endpoint for API testing
2. **Database Inspection**: Connect directly to PostgreSQL to verify data
3. **Container Logs**: `docker-compose logs [service]` for error details
4. **Service Health**: Verify all services are running and ready

## 📝 Code Review Checklist

### React Flow Components
- [ ] Parameter changes update both local state and ReactFlow nodes
- [ ] useEffect syncs external data changes to local state
- [ ] useCallback dependencies include all required values
- [ ] Component handles loading and error states

### API Integration
- [ ] Proper error handling with try/catch or React Query error states
- [ ] Loading states for all async operations
- [ ] Authentication headers attached to requests
- [ ] Response data properly typed with TypeScript

### Database Operations
- [ ] Models include proper relationships and constraints
- [ ] Migrations tested with nuclear reset approach
- [ ] Seed data matches frontend expectations
- [ ] Foreign key relationships properly maintained

## 🚨 Common Pitfalls

### ❌ React Flow Anti-Patterns
```typescript
// DON'T: Only update local state
const handleChange = (value) => {
  setLocalState(value) // This won't be saved!
}

// DON'T: Missing useEffect for external changes
// Component won't sync when data prop changes
```

### ❌ Database Management Anti-Patterns
```bash
# DON'T: Try to fix broken migrations incrementally
alembic downgrade -1
alembic upgrade head

# DO: Use nuclear reset for development
docker-compose down -v && ./setup.sh
```

### ❌ API Integration Anti-Patterns
```typescript
// DON'T: Ignore loading and error states
const { data } = useQuery(...)
return <div>{data.map(...)}</div> // Will crash if data is undefined

// DON'T: Forget authentication dependency
// Routes that require auth must use ProtectedRoute wrapper
```

## 🎯 Success Metrics

### Performance Indicators
- **Build Time**: Frontend builds complete without TypeScript errors
- **API Response Time**: All endpoints respond within 200ms locally
- **State Consistency**: Parameter changes persist correctly through save/load cycles
- **Error Handling**: Graceful degradation for all failure scenarios

### User Experience Indicators
- **Parameter Persistence**: UI changes survive page refresh after save
- **Loading States**: No jarring transitions or undefined data displays  
- **Error Recovery**: Clear error messages with actionable next steps
- **Navigation Flow**: Intuitive routing between dashboard, workflows, and products

## 🔮 Future Considerations

### Scalability Patterns
- **Component Library**: Extract common patterns into reusable components
- **State Management**: Consider upgrading from localStorage to more robust state management
- **API Optimization**: Implement pagination for large datasets
- **Caching Strategy**: Optimize React Query cache invalidation patterns

### Maintenance Strategies
- **Documentation**: Keep this file updated with new patterns and lessons
- **Testing**: Add automated tests for critical state synchronization patterns
- **Monitoring**: Implement error tracking for production deployment
- **Performance**: Monitor bundle size and loading performance

---

**Note**: This document should be updated whenever significant patterns are discovered, critical bugs are resolved, or new development strategies are established. It serves as the collective memory for AI-assisted development on this repository.