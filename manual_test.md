# Manual Backend Testing Guide

## Test URLs
Base URL: `https://backend-prod-dun.vercel.app`

### 1. Basic Health Check
```
GET https://backend-prod-dun.vercel.app/
```
Expected: JSON response with status "healthy"

### 2. API Health Check  
```
GET https://backend-prod-dun.vercel.app/api/health
```
Expected: JSON response with status "healthy"

### 3. Waitlist Endpoint (Main Issue)
```
GET https://backend-prod-dun.vercel.app/api/waitlist
```
Expected: JSON response with "Waitlist endpoint working"

### 4. Test Endpoint
```
GET https://backend-prod-dun.vercel.app/api/test
```
Expected: JSON response with CORS origins

### 5. API Documentation
```
GET https://backend-prod-dun.vercel.app/api/docs
```
Expected: JSON response with all available endpoints

## How to Test

### Using Browser
1. Open browser
2. Navigate to any URL above
3. Should see JSON response (not 404 error)

### Using curl (if available)
```bash
curl -X GET "https://backend-prod-dun.vercel.app/api/waitlist" -H "Accept: application/json"
```

### Using PowerShell
```powershell
Invoke-RestMethod -Uri "https://backend-prod-dun.vercel.app/api/waitlist" -Method Get
```

### Using Postman/Insomnia
1. Create new GET request
2. URL: `https://backend-prod-dun.vercel.app/api/waitlist`
3. Headers: `Accept: application/json`
4. Send request

## Expected Results

### If Working (200 OK):
```json
{
  "message": "Waitlist endpoint working",
  "status": "ready for implementation",
  "timestamp": "2024-01-11T12:00:00Z"
}
```

### If Not Working (404 NOT FOUND):
```
404: NOT_FOUND
Code: NOT_FOUND
ID: sfo1::xxxx-timestamp-xxxx
```

## Common Issues and Solutions

### 1. 404 Not Found
- Backend not deployed with latest changes
- Route not properly configured
- **Solution**: Redeploy backend to Vercel

### 2. CORS Error
- Frontend domain not in CORS allow list
- **Solution**: Check CORS configuration in backend

### 3. 500 Internal Server Error
- Backend code error
- **Solution**: Check Vercel function logs

## Deployment Commands

### To deploy backend:
```bash
cd backend-prod
vercel --prod
```

### To check deployment status:
```bash
vercel ls
```

### To view logs:
```bash
vercel logs
``` 