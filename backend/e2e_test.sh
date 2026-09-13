#!/bin/bash
set -e
BASE=http://localhost:8000/api/v1

echo "== 1. Admin login =="
ADMIN_TOKEN=$(curl -s -X POST $BASE/auth/login -H "Content-Type: application/json" -d '{"email":"admin@offpeak.app","password":"demo1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "admin token ok"

echo "== 2. Admin sees pending application =="
APP_ID=$(curl -s $BASE/admin/applications -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -c "import sys,json; d=json.load(sys.stdin); print([a['id'] for a in d if a['status']=='PENDING'][0])")
echo "pending application id: $APP_ID"

echo "== 3. Admin approves application =="
curl -s -X POST $BASE/admin/applications/$APP_ID/approve -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d '{"notes":"Looks good"}' | python3 -m json.tool

echo "== 4. Restaurant (Luna Bistro) login =="
REST_TOKEN=$(curl -s -X POST $BASE/auth/login -H "Content-Type: application/json" -d '{"email":"luna@offpeak.app","password":"demo1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "restaurant token ok"

echo "== 5. Restaurant generates revenue recommendation =="
REC=$(curl -s -X POST $BASE/restaurants/me/recommendations/generate -H "Authorization: Bearer $REST_TOKEN")
echo "$REC" | python3 -m json.tool
REC_ID=$(echo "$REC" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "== 6. Restaurant creates offer FROM recommendation =="
NEW_OFFER=$(curl -s -X POST $BASE/restaurants/me/recommendations/$REC_ID/create-offer -H "Authorization: Bearer $REST_TOKEN" -H "Content-Type: application/json" -d '{"recommendation_id":"'"$REC_ID"'","max_redemptions":20}')
echo "$NEW_OFFER" | python3 -m json.tool

echo "== 7. Diner: send + verify OTP =="
curl -s -X POST $BASE/auth/send-otp -H "Content-Type: application/json" -d '{"phone_number":"+61400000000"}' | python3 -m json.tool
DINER_TOKEN=$(curl -s -X POST $BASE/auth/verify-otp -H "Content-Type: application/json" -d '{"phone_number":"+61400000000","code":"123456"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "diner token ok"

echo "== 8. Diner discovers offers =="
curl -s $BASE/offers | python3 -m json.tool | head -40

echo "== 9. Diner claims the seeded active offer (Luna Pasta Special) =="
OFFER_ID=$(curl -s $BASE/offers | python3 -c "import sys,json; d=json.load(sys.stdin); print([o['id'] for o in d if 'Pasta' in o['title']][0])")
CLAIM=$(curl -s -X POST $BASE/claims/offers/$OFFER_ID -H "Authorization: Bearer $DINER_TOKEN")
echo "$CLAIM" | python3 -m json.tool
CLAIM_ID=$(echo "$CLAIM" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
REDEMPTION_CODE=$(echo "$CLAIM" | python3 -c "import sys,json; print(json.load(sys.stdin)['redemption_code'])")

echo "== 10. Restaurant redeems the claim =="
curl -s -X POST $BASE/claims/redeem -H "Authorization: Bearer $REST_TOKEN" -H "Content-Type: application/json" -d '{"redemption_code":"'"$REDEMPTION_CODE"'"}' | python3 -m json.tool

echo "== 11. Diner completes simulated checkout (\$120 bill) =="
TXN=$(curl -s -X POST $BASE/transactions -H "Authorization: Bearer $DINER_TOKEN" -H "Content-Type: application/json" -d '{"claim_id":"'"$CLAIM_ID"'","original_amount_cents":12000}')
echo "$TXN" | python3 -m json.tool

echo "== 12. Diner wallet / loyalty =="
curl -s $BASE/loyalty -H "Authorization: Bearer $DINER_TOKEN" | python3 -m json.tool

echo "== 13. Restaurant analytics =="
curl -s $BASE/restaurants/me/analytics -H "Authorization: Bearer $REST_TOKEN" | python3 -m json.tool

echo "== 14. Admin dashboard =="
curl -s $BASE/admin/dashboard -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool

echo "== ALL STEPS COMPLETE =="
