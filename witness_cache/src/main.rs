use accumulator::group::Rsa2048;
use accumulator::{Accumulator, Witness};
use std::thread;
extern crate stopwatch;
use rand::Rng;
use stopwatch::Stopwatch;
mod exps;

fn main() {
    // The count of all supported system states
    const STATE_COUNT: usize = 32; // (usize::MAX >> 58) + 1;
    const NUM_TO_UPD: usize = 16;         //[256, 512, 1024, 2048]
    const NEW_STATE_COUNT: usize = 2;  //[128, 256, 512, 1024, 2048]
    const DEL_STATE_COUNT: usize = 2;
    const THREAD_COUNT: usize = 4;

    println!("usize {}", STATE_COUNT);

    // generate sorted (in decending order) random access frequencies to each state
    // let mut rng = rand::thread_rng();
    // let mut frequencies: Vec<u64> = (0..STATE_COUNT - 1)
    //     .map(|_| rng.gen_range(0..100))
    //     .collect();
    // frequencies.sort_by(|a, b| b.cmp(a));

    // Initialize the accumulator
    // Add all states (key-value pairs) into the accumulator.
    let mut states: Vec<String> = Vec::new();
    for i in 0..STATE_COUNT {
        states.push(format!("{} : {}", i, i));
    }
    let states: Vec<&str> = states.iter().map(|s| s as &str).collect();
    let acc = Accumulator::<Rsa2048, &str>::empty();
    let (acc, proof) = acc.add_with_proof(&states);

    // Generate witness for each state and store in the array.
    let non_cache_witness: Vec<(&str, Witness<Rsa2048, &str>)> = proof.witness.compute_individual_witnesses(&states);

    // Partition the witnesses for each thread
    let mut non_cache_witness_td: Vec<Vec<(&str, Witness<Rsa2048, &str>)>> = Vec::new();
    let steps:usize = (NUM_TO_UPD/THREAD_COUNT).try_into().unwrap();
    for i in 0..THREAD_COUNT {
        non_cache_witness_td.push(non_cache_witness[(i*steps)..((i+1)*steps)].to_vec());
    }

    // prepare for del exp
    // let witnesses = non_cache_witness.to_vec();
    // let del_acc = acc.clone();

    // -------------------------------------------------------------
    // test the time of witness update when adding new states
    // -------------------------------------------------------------
    let mut new_states: Vec<String> = Vec::new();
    for i in 0..NEW_STATE_COUNT {
        new_states.push(format!("{} : {}", i + STATE_COUNT, i + STATE_COUNT));
    }
    let new_states: Vec<&str> = new_states.iter().map(|s| s as &str).collect();
    // let mut upd_non_cache_witness: Vec<(&str, Witness<Rsa2048, &str>)> = Vec::new();

    // add new states into the accumulator and update the witness for each state
    let acc = acc.add(&new_states);
    // let mut upd_count: usize = 0;

    let sw = Stopwatch::start_new();
    // for (st, wit) in non_cache_witness {
    //     if upd_count >= NUM_TO_UPD {
    //         continue;
    //     }
    //     upd_count = upd_count + 1;
    //     let upd_wit = acc.update_membership_witness(wit, &[st], &new_states, &[]);
    //     match upd_wit {
    //         Ok(wit) => upd_non_cache_witness.push((st, wit)),
    //         Err(e) => println!("error: {:?}", e),
    //     }
    // }

    let handles = (0..THREAD_COUNT)
        .into_iter()
        .map(|i| {
            println!("Created thread {}", i);
            // thread::spawn(move || update_witness_after_addition(&non_cache_witness_td[i], &acc, &new_states))
            thread::spawn(move || test(&non_cache_witness_td[i]))
        })
        .collect::<Vec<_>>();
    println!("waiting ...");
    handles.into_iter().for_each(|h| h.join().unwrap());

    println!(
        "Update {} witnesses after adding {} states took {}ms",
        NUM_TO_UPD,
        NEW_STATE_COUNT,
        sw.elapsed_ms()
    );

    // assert the updated witness is correct
    let membership = acc.prove_membership(&non_cache_witness_td[0][1..2]);
    match membership {
        Ok(proof) => assert!(acc.verify_membership_batch(&["1 : 1"], &proof)),
        Err(e) => println!("error: {:?}", e),
    }

    // -------------------------------------------------------------
    // test the time of witness update when delete existing states
    // -------------------------------------------------------------
    let acc = del_acc;
    let mut del_states: Vec<String> = Vec::new();
    for i in STATE_COUNT - DEL_STATE_COUNT..STATE_COUNT {
        del_states.push(format!("{} : {}", i, i));
    }
    let del_states: Vec<&str> = del_states.iter().map(|s| s as &str).collect();
    let mut upd2_non_cache_witness: Vec<(&str, Witness<Rsa2048, &str>)> = Vec::new();

    // delete states from the accumulator and update the witness for each state
    let del_res = acc.delete(&witnesses[STATE_COUNT - DEL_STATE_COUNT..STATE_COUNT]);

    let mut upd_count: i32 = 0;

    match del_res {
        Ok(acc) => {
            let sw = Stopwatch::start_new();
            for (st, wit) in witnesses {
                if del_states.contains(&st) || upd_count >= NUM_TO_UPD {
                    continue;
                }
                upd_count = upd_count + 1;
                let upd_wit_res = acc.update_membership_witness(wit, &[st], &[], &del_states);
                match upd_wit_res {
                    Ok(upd_wit) => upd2_non_cache_witness.push((st, upd_wit)),
                    Err(e) => println!("error: {:?}", e),
                }
            }
            println!(
                "Update {} witnesses after deleting {} states took {}ms",
                upd2_non_cache_witness.len(),
                DEL_STATE_COUNT,
                sw.elapsed_ms()
            );
            // assert the updated witness is correct
            let membership = acc.prove_membership(&upd2_non_cache_witness[1..2]);
            match membership {
                Ok(proof) => assert!(acc.verify_membership_batch(&["1 : 1"], &proof)),
                Err(e) => println!("error: {:?}", e),
            }
        }
        Err(e) => println!("error: {:?}", e),
    }
}

// fn main() {
//     const THREAD_COUNT: usize = 4;
//     const STATE_COUNT: usize = 4096; // (usize::MAX >> 58) + 1;
//     const NUM_TO_UPD: usize = 2048; //[256, 512, 1024, 2048]
//     const NEW_STATE_COUNT: usize = 512; //[128, 256, 512, 1024, 2048]

//     let overall_sw = Stopwatch::start_new();

//     let handles = (0..THREAD_COUNT)
//         .into_iter()
//         .map(|i| {
//             println!("Created thread {}", i);
//             // thread::spawn(move || update_witness_after_addition(&non_cache_witness_td[i], &acc, &new_states))
//             thread::spawn(move || {
//                 test(
//                     i,
//                     STATE_COUNT / THREAD_COUNT as usize,
//                     NUM_TO_UPD / THREAD_COUNT as usize,
//                     NEW_STATE_COUNT,
//                 )
//             })
//         })
//         .collect::<Vec<_>>();
//     println!("waiting ...");
//     handles.into_iter().for_each(|h| h.join().unwrap());

//     println!(
//         "Update {} witnesses after adding {} states with {} existing states took overall {}ms. Remember to compute the percentage!",
//         NUM_TO_UPD,
//         NEW_STATE_COUNT,
//         STATE_COUNT,
//         overall_sw.elapsed_ms(),
//     );
// }

fn update_witness_after_addition(
    witness: &Vec<(&str, Witness<Rsa2048, &str>)>,
    acc: &Accumulator<Rsa2048, &str>,
    new_states: &[&str],
) { // -> Vec<(&'a str, Witness<Rsa2048, &'a str>)> {
    let mut upd_witness: Vec<(&str, Witness<Rsa2048, &str>)> = Vec::new();

    for (st, wit) in witness {
        let upd_wit_res = acc.update_membership_witness(wit, &[st], new_states, &[]);
        match upd_wit_res {
            Ok(upd_wit) => {
                if st == "1 : 1"{
                    let membership = acc.prove_membership(&[(st, upd_wit)]);
                    match membership {
                        Ok(proof) => assert!(acc.verify_membership_batch(&["1 : 1"], &proof)),
                        Err(e) => println!("error: {:?}", e),
                    }
                }
            },// upd_witness.push((st, upd_wit)),
            Err(e) => println!("error: {:?}", e),
        }
    }
}

fn test(t_id: usize, STATE_COUNT: usize, NUM_TO_UPD: usize, NEW_STATE_COUNT: usize) {
    // const DEL_STATE_COUNT: usize = 2;

    let total_sw = Stopwatch::start_new();

    // Initialize the accumulator
    // Add all states (key-value pairs) into the accumulator.
    let mut states: Vec<String> = Vec::new();
    for i in 0..STATE_COUNT {
        states.push(format!("{} : {}", i, i));
    }
    let states: Vec<&str> = states.iter().map(|s| s as &str).collect();
    let acc = Accumulator::<Rsa2048, &str>::empty();
    let (acc, proof) = acc.add_with_proof(&states);

    // Generate witness for each state and store in the array.
    let non_cache_witness: Vec<(&str, Witness<Rsa2048, &str>)> =
        proof.witness.compute_individual_witnesses(&states);

    // prepare for del exp
    // let witnesses = non_cache_witness.to_vec();
    // let del_acc = acc.clone();

    // -------------------------------------------------------------
    // test the time of witness update when adding new states
    // -------------------------------------------------------------
    let mut new_states: Vec<String> = Vec::new();
    for i in 0..NEW_STATE_COUNT {
        new_states.push(format!("{} : {}", i + STATE_COUNT, i + STATE_COUNT));
    }
    let new_states: Vec<&str> = new_states.iter().map(|s| s as &str).collect();
    let mut upd_non_cache_witness: Vec<(&str, Witness<Rsa2048, &str>)> = Vec::new();

    // add new states into the accumulator and update the witness for each state
    let acc = acc.add(&new_states);
    let mut upd_count: usize = 0;

    let sw = Stopwatch::start_new();
    for (st, wit) in non_cache_witness {
        if upd_count >= NUM_TO_UPD {
            continue;
        }
        upd_count = upd_count + 1;
        let upd_wit = acc.update_membership_witness(wit, &[st], &new_states, &[]);
        match upd_wit {
            Ok(wit) => upd_non_cache_witness.push((st, wit)),
            Err(e) => println!("error: {:?}", e),
        }
    }

    println!(
        "Thread {} update {} witnesses after adding {} states took {}ms vs. total cost {}ms",
        t_id,
        NUM_TO_UPD,
        NEW_STATE_COUNT,
        sw.elapsed_ms(),
        total_sw.elapsed_ms(),
    );
}
