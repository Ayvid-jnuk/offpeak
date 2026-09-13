export type Role = "DINER" | "RESTAURANT" | "ADMIN";

export interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  address: string;
  description: string;
  phone: string;
  email: string;
  opening_hours: string;
  seating_capacity: number;
  image_url: string | null;
  rating: number;
  is_active: boolean;
}

export interface RestaurantApplication {
  id: string;
  name: string;
  cuisine: string;
  address: string;
  description: string;
  phone: string;
  email: string;
  opening_hours: string;
  seating_capacity: number;
  image_url: string | null;
  status: "PENDING" | "APPROVED" | "REJECTED";
  created_at: string;
  reviewed_at: string | null;
}

export interface Offer {
  id: string;
  restaurant_id: string;
  title: string;
  description: string | null;
  discount_percent: number;
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  max_redemptions: number;
  redemptions_used: number;
  status: "ACTIVE" | "INACTIVE" | "EXPIRED";
  created_at: string;
}

export interface OfferWithRestaurant extends Offer {
  restaurant_name: string;
  restaurant_cuisine: string;
  restaurant_rating: number;
  restaurant_image_url: string | null;
}

export interface Claim {
  id: string;
  offer_id: string;
  diner_id: string;
  redemption_code: string;
  status: "CLAIMED" | "REDEEMED" | "EXPIRED" | "CANCELLED";
  claimed_at: string;
  redeemed_at: string | null;
}

export interface Transaction {
  id: string;
  claim_id: string;
  offer_id: string;
  diner_id: string;
  restaurant_id: string;
  original_amount_cents: number;
  discount_amount_cents: number;
  final_amount_cents: number;
  platform_commission_cents: number;
  restaurant_payout_cents: number;
  currency: string;
  status: string;
  created_at: string;
}

export interface LoyaltyTxn {
  id: string;
  type: "EARNED" | "REDEEMED" | "ADJUSTED";
  points: number;
  reason: string;
  created_at: string;
}

export interface LoyaltyAccount {
  points_balance: number;
  lifetime_points_earned: number;
  credits_available_cents: number;
  recent_activity: LoyaltyTxn[];
}

export interface Recommendation {
  id: string;
  restaurant_id: string;
  day_of_week: number;
  window_start_hour: number;
  window_end_hour: number;
  historical_occupancy_pct: number;
  available_capacity: number;
  recommended_discount_percent: number;
  estimated_additional_covers: number;
  estimated_incremental_revenue_cents: number;
  rationale: string;
  was_used_for_offer: boolean;
  created_at: string;
}

export interface RestaurantAnalytics {
  today_revenue_cents: number;
  offer_revenue_cents: number;
  redemption_rate_pct: number;
  average_transaction_cents: number;
  estimated_incremental_revenue_cents: number;
  unused_capacity_pct: number;
  best_performing_offer: string | null;
  best_performing_time_window: string | null;
  total_claims: number;
  total_redemptions: number;
}

export interface AdminDashboard {
  restaurants: number;
  pending_applications: number;
  active_offers: number;
  claims: number;
  transactions: number;
  gross_transaction_value_cents: number;
  platform_commission_cents: number;
  active_diners: number;
}

export const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export function cents(c: number): string {
  return `$${(c / 100).toFixed(2)}`;
}
