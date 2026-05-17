// Run tests.c by following the instructions below:

// This file contains passing tests.

// Run them by opening a terminal and running the following:
// $ make -B Season-1/Level-2/tests && ./Season-1/Level-2/tests

#include "code.h"
#include <assert.h>

int main() {
    printf("Level 2 \n\n");

    // Create a non-admin user
    int user1 = create_user_account(false, "pwned");
    printf("0. Non-admin (admin:%i) username called '%s' has been created \n\n", is_admin(user1), username(user1));
    assert(is_admin(user1) == false);
    assert(strcmp(username(user1), "pwned") == 0);

    // Create an admin user
    int admin1 = create_user_account(true, "admin");
    assert(is_admin(admin1) == true);
    assert(strcmp(username(admin1), "admin") == 0);

    // Non-admin can update valid settings
    printf("1. Non-admin users like '%s' can update some dummy numerical settings \n", username(user1));
    bool result = update_setting(user1, "1", "10");
    assert(result == true);
    printf("3. Dummy setting '1' has been now set to dummy number '10' for user '%s' \n", username(user1));

    // Non-admin must not be escalated by negative index
    printf("2. Non-admin users have no access to settings that can escalate themselves to admins \n\n");
    bool neg_result = update_setting(user1, "-7", "1");
    assert(neg_result == false);
    assert(is_admin(user1) == false);
    printf("4. Making sure user '%s' is not an admin after negative-index attempt -> Admin:%i \n\n", username(user1), is_admin(user1));

    // Out-of-bounds positive index must be rejected
    bool oob_result = update_setting(user1, "10", "99");
    assert(oob_result == false);

    // Invalid (non-numeric) index must be rejected
    bool invalid_result = update_setting(user1, "abc", "1");
    assert(invalid_result == false);

    // Invalid user_id must be handled safely
    bool bad_user = update_setting(-1, "1", "1");
    assert(bad_user == false);

    printf("All assertions passed. CONGRATULATIONS LEVEL 2 PASSED!\n");
    return 0;
}
