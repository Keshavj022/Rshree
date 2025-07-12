import streamlit as st
import random
from collections import Counter

COUPON_VALUES = [250, 500, 1000, 2000]

def generate_coupon_distribution(target_amount, num_coupons):
    """
    Generate a distribution of coupon values that sum to target_amount
    for the given number of coupons
    """
    if target_amount < num_coupons * min(COUPON_VALUES):
        return None
    
    # Start with minimum values for all coupons
    distribution = [min(COUPON_VALUES)] * num_coupons
    remaining = target_amount - sum(distribution)
    
    # Randomly distribute the remaining amount
    for i in range(num_coupons):
        if remaining <= 0:
            break
        
        # Calculate maximum we can add to this position
        current_value = distribution[i]
        possible_upgrades = [v for v in COUPON_VALUES if v > current_value]
        
        if possible_upgrades and remaining > 0:
            # Choose a random upgrade that doesn't exceed remaining budget
            valid_upgrades = [v for v in possible_upgrades if (v - current_value) <= remaining]
            
            if valid_upgrades:
                new_value = random.choice(valid_upgrades)
                remaining -= (new_value - current_value)
                distribution[i] = new_value
    
    # Final adjustment to exactly match target
    attempts = 0
    while sum(distribution) != target_amount and attempts < 1000:
        attempts += 1
        for i in range(num_coupons):
            current_sum = sum(distribution)
            if current_sum == target_amount:
                break
            
            diff = target_amount - current_sum
            current_value = distribution[i]
            
            if diff > 0:
                # Need to increase
                possible_increases = [v for v in COUPON_VALUES if v > current_value and (v - current_value) <= diff]
                if possible_increases:
                    distribution[i] = random.choice(possible_increases)
            elif diff < 0:
                # Need to decrease
                possible_decreases = [v for v in COUPON_VALUES if v < current_value and (current_value - v) <= abs(diff)]
                if possible_decreases:
                    distribution[i] = random.choice(possible_decreases)
    
    return distribution

def generate_alternative_combinations(target_amount, num_coupons, num_alternatives=5):
    """Generate multiple different combinations that achieve the same target amount"""
    alternatives = []
    max_attempts = 100
    
    for _ in range(max_attempts):
        distribution = generate_coupon_distribution(target_amount, num_coupons)
        if distribution and sum(distribution) == target_amount:
            # Convert to sorted tuple for comparison (to avoid duplicates)
            sorted_dist = tuple(sorted(distribution))
            if sorted_dist not in [tuple(sorted(alt)) for alt in alternatives]:
                alternatives.append(distribution)
                if len(alternatives) >= num_alternatives:
                    break
    
    return alternatives

def display_coupon_summary(distribution):
    """Display coupon distribution as count summary"""
    coupon_counts = Counter(distribution)
    
    st.subheader("🎫 Coupon Distribution Summary")
    
    total_value = 0
    for value in sorted(coupon_counts.keys()):
        count = coupon_counts[value]
        value_total = value * count
        total_value += value_total
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.write(f"₹{value:,} coupons")
        with col2:
            st.write(f"**{count}** pieces")
        with col3:
            st.write(f"Total: ₹{value_total:,}")
    
    st.divider()
    st.metric("Total Distributed Amount", f"₹{total_value:,}")

def display_alternative_combinations(alternatives, target_amount):
    """Display 5 alternative combinations"""
    if len(alternatives) > 1:
        st.subheader("🔄 Alternative Combinations")
        st.markdown(f"Here are {len(alternatives)} different ways to distribute ₹{target_amount:,}:")
        
        for i, alt in enumerate(alternatives, 1):
            with st.expander(f"Combination {i}"):
                coupon_counts = Counter(alt)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Distribution:**")
                    for value in sorted(coupon_counts.keys()):
                        count = coupon_counts[value]
                        st.write(f"• {count} × ₹{value:,} = ₹{count * value:,}")
                
                with col2:
                    st.write("**Summary:**")
                    st.metric("Total Coupons", len(alt))
                    st.metric("Total Value", f"₹{sum(alt):,}")
    else:
        st.info("💡 Only one unique combination found for this target amount and coupon count.")

# Streamlit App
st.set_page_config(
    page_title="Coupon Generator",
    page_icon="🎫",
    layout="centered"
)

st.title("🎫 Coupon Code Generator")
st.markdown("Generate random coupon distributions for your target amount")

# Input Section
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        target_amount = st.number_input(
            "Target Prize Amount (₹)",
            min_value=1,
            step=1,
            help="Total amount to be distributed across all coupons"
        )
    
    with col2:
        num_coupons = st.number_input(
            "Number of Coupons",
            min_value=1,
            step=1,
            help="How many coupons to generate"
        )

# Available coupon values info
with st.expander("Available Coupon Values"):
    st.write("The following coupon values are available:")
    cols = st.columns(len(COUPON_VALUES))
    for i, value in enumerate(COUPON_VALUES):
        with cols[i]:
            st.metric("", f"₹{value:,}")

# Generate Button
if st.button("Generate Coupons", type="primary", use_container_width=True):
    if target_amount and num_coupons:
        min_possible = num_coupons * min(COUPON_VALUES)
        
        if target_amount < min_possible:
            st.error(f"❌ Target amount too low! Minimum required: ₹{min_possible:,} for {num_coupons} coupons")
        else:
            with st.spinner("Generating coupon distribution..."):
                distribution = generate_coupon_distribution(target_amount, num_coupons)
                
                if distribution and sum(distribution) == target_amount:
                    st.success("✅ Coupons generated successfully!")
                    display_coupon_summary(distribution)
                    
                    # Generate and display alternative combinations
                    with st.spinner("Finding alternative combinations..."):
                        alternatives = generate_alternative_combinations(target_amount, num_coupons, 5)
                        display_alternative_combinations(alternatives, target_amount)
                    
                    # Additional details in expander
                    with st.expander("View Individual Coupon Values"):
                        st.write("Individual coupon values (shuffled):")
                        cols = st.columns(5)
                        for i, value in enumerate(distribution):
                            with cols[i % 5]:
                                st.write(f"#{i+1}: ₹{value:,}")
                                
                else:
                    st.error("❌ Could not generate exact distribution. Try adjusting the target amount.")
    else:
        st.warning("⚠️ Please enter both target amount and number of coupons")

# Footer
st.markdown("---")
st.markdown("*Coupon values: ₹250, ₹500, ₹1,000, ₹2,000*")