package com.interviewiq.progress.repository;

import com.interviewiq.progress.model.StudyProgress;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProgressRepository extends JpaRepository<StudyProgress, Long> {

    List<StudyProgress> findByUserId(String userId);

    Optional<StudyProgress> findByUserIdAndTopicName(
            String userId,
            String topicName
    );
}