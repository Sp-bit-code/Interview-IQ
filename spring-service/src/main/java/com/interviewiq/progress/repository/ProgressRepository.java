package com.interviewiq.progress.repository;

import com.interviewiq.progress.model.StudyProgress;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

@Repository
public class ProgressRepository {

    private final List<StudyProgress> progressList = new ArrayList<>();

    private final AtomicLong idGenerator = new AtomicLong(1);


    // Get all progress records for a user
    public List<StudyProgress> findByUserId(String userId) {

        return progressList
                .stream()
                .filter(progress ->
                        progress.getUserId().equals(userId)
                )
                .toList();
    }


    // Find one progress record by user and topic
    public Optional<StudyProgress> findByUserIdAndTopicName(
            String userId,
            String topicName
    ) {

        return progressList
                .stream()
                .filter(progress ->
                        progress.getUserId().equals(userId)
                                &&
                        progress.getTopicName().equals(topicName)
                )
                .findFirst();
    }


    // Save new progress or update existing progress
    public StudyProgress save(StudyProgress progress) {

        if (progress.getId() == null) {

            progress.setId(
                    idGenerator.getAndIncrement()
            );

            progressList.add(progress);

            return progress;
        }


        for (int i = 0; i < progressList.size(); i++) {

            StudyProgress existingProgress =
                    progressList.get(i);

            if (existingProgress
                    .getId()
                    .equals(progress.getId())) {

                progressList.set(i, progress);

                return progress;
            }
        }


        progressList.add(progress);

        return progress;
    }


    // Delete progress by ID
    public void deleteById(Long id) {

        progressList.removeIf(
                progress ->
                        progress.getId().equals(id)
        );
    }
}
