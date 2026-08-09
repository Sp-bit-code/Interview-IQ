package com.interviewiq.progress.service;

import com.interviewiq.progress.model.StudyProgress;
import com.interviewiq.progress.repository.ProgressRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProgressService {

    private final ProgressRepository progressRepository;

    // Constructor Injection
    public ProgressService(ProgressRepository progressRepository) {
        this.progressRepository = progressRepository;
    }

    public List<StudyProgress> getUserProgress(String userId) {
        return progressRepository.findByUserId(userId);
    }

    public StudyProgress saveOrUpdateProgress(StudyProgress progress) {

        return progressRepository
                .findByUserIdAndTopicName(
                        progress.getUserId(),
                        progress.getTopicName()
                )
                .map(existingProgress -> {

                    existingProgress.setCompleted(progress.getCompleted());

                    return progressRepository.save(existingProgress);
                })
                .orElseGet(() -> progressRepository.save(progress));
    }

    public long getCompletedTopicCount(String userId) {

        return progressRepository
                .findByUserId(userId)
                .stream()
                .filter(progress ->
                        Boolean.TRUE.equals(progress.getCompleted())
                )
                .count();
    }

    public void deleteProgress(Long id) {
        progressRepository.deleteById(id);
    }
}