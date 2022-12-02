use accumulator::group::Rsa2048;
use accumulator::{Accumulator, Witness};
extern crate stopwatch;
use stopwatch::Stopwatch;

// test the time of witness update (non cache is used) when new states are added
// INPUT: the count of states to add, current accumulator, current witnesses vec
// OUTPUT: result conatining updated witnesses vec
pub fn upd_witness_after_addition(NEW_STATE_COUNT: usize, STATE_COUNT: usize, NUM_TO_UPD: i32) {
    // Initialize the accumulator
    // Add all states (key-value pairs) into the accumulator.
    let mut states: Vec<&str> = Vec::new();
    for i in 0..STATE_COUNT {
        states.push("test"); //(format!("{} : {}", i, i));
    }
    // let states: Vec<&'static str> = states.iter().map(|s| s as &'static str).collect();

    let acc = Accumulator::<Rsa2048, &'static str>::empty();
    let (acc, proof) = acc.add_with_proof(&states);

    // Generate witness for each state and store in the array.
    let non_cache_witness: Vec<(&str, Witness<Rsa2048, &str>)> =
        proof.witness.compute_individual_witnesses(&states);

    // generate new states to add
    let mut new_states: Vec<String> = Vec::new();
    for i in 0..NEW_STATE_COUNT {
        new_states.push(format!("{} : {}", i + states.len(), i + states.len()));
    }
    let new_states: Vec<&str> = new_states.iter().map(|s| s as &str).collect();
    let mut upd_witness: Vec<(&str, Witness<Rsa2048, &str>)> = Vec::new();

    // add new states into the accumulator and update the witness for each state
    let acc = acc.add(&new_states);
    let mut upd_count: i32 = 0;

    let sw = Stopwatch::start_new();
    for (st, wit) in non_cache_witness {
        if upd_count >= NUM_TO_UPD {
            continue;
        }
        upd_count = upd_count + 1;
        let upd_wit = acc.update_membership_witness(wit, &[st], &new_states, &[]);
        match upd_wit {
            Ok(wit) => upd_witness.push((st, wit)),
            Err(e) => println!("error: {:?}", e),
        }
    }
    println!(
        "Update {} witnesses after adding {} states took {}ms",
        upd_witness.len(),
        NEW_STATE_COUNT,
        sw.elapsed_ms()
    );

    // assert the updated witness is correct
    let membership = acc.prove_membership(&upd_witness[1..2]);
    match membership {
        Ok(proof) => assert!(acc.verify_membership_batch(&["1 : 1"], &proof)),
        Err(e) => println!("error: {:?}", e),
    }
    println!("Finish the test of witness update after addition")
}

// pub fn upd_witness_after_removal(DEL_STATE_COUNT:usize, states:Vec<&str> , cur_acc: Accumulator::<Rsa2048, &'static str>, cur_witnesses:Vec<(&str, Witness<Rsa2048, &str>)>){
//     let STATE_COUNT = states.len();
//     let acc = del_acc;
//     let mut del_states: Vec<String> = Vec::new();
//     for i in STATE_COUNT - DEL_STATE_COUNT..STATE_COUNT {
//         del_states.push(format!("{} : {}", i, i));
//     }
//     let del_states: Vec<&str> = del_states.iter().map(|s| s as &str).collect();
//     let mut upd2_non_cache_witness: Vec<(&str, Witness<Rsa2048, &str>)> = Vec::new();

//     // delete states from the accumulator and update the witness for each state
//     let del_res = acc.delete(&witnesses[STATE_COUNT - DEL_STATE_COUNT..STATE_COUNT]);

//     let mut upd_count: i32 = 0;

//     match del_res {
//         Ok(acc) => {
//             let sw = Stopwatch::start_new();
//             for (st, wit) in witnesses {
//                 if del_states.contains(&st) || upd_count >= NUM_TO_UPD {
//                     continue;
//                 }
//                 upd_count = upd_count + 1;
//                 let upd_wit_res = acc.update_membership_witness(wit, &[st], &[], &del_states);
//                 match upd_wit_res {
//                     Ok(upd_wit) => upd2_non_cache_witness.push((st, upd_wit)),
//                     Err(e) => println!("error: {:?}", e),
//                 }
//             }
//             println!(
//                 "Update {} witnesses after deleting {} states took {}ms",
//                 upd2_non_cache_witness.len(),
//                 DEL_STATE_COUNT,
//                 sw.elapsed_ms()
//             );
//             // assert the updated witness is correct
//             let membership = acc.prove_membership(&upd2_non_cache_witness[1..2]);
//             match membership {
//                 Ok(proof) => assert!(acc.verify_membership_batch(&["1 : 1"], &proof)),
//                 Err(e) => println!("error: {:?}", e),
//             }
//         }
//         Err(e) => println!("error: {:?}", e),
//     }
// }
